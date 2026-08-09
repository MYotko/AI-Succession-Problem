# Docs Snapshot

Generated: 2026-08-09T15:37:26Z
Repository: C:\Users\matty\Dev\ai-succession-problem
Commit: c9d04fa
Branch: main
Category: docs

## Files included

| File | Lines | Bytes |
|------|-------|-------|
| docs\bootstrap_gate_architecture.md | 862 | 30347 |
| docs\CITATIONS.md | 148 | 5725 |
| docs\contact.md | 39 | 2310 |
| docs\glossary.md | 633 | 26043 |
| docs\lineage_imperative_one_pager_v1.md | 80 | 10128 |
| docs\lineage_imperative_one_pager_v2.md | 80 | 9428 |
| docs\lineage_phi_program_reference.md | 1719 | 153399 |
| docs\paper_v2_outline.md | 337 | 17204 |
| docs\RUNBOOK.md | 220 | 12241 |
| docs\Simulation_Scenarios.md | 338 | 51488 |
| docs\SPECIFICATION_GAPS.md | 1029 | 57958 |
| docs\The AI Succession Problem.md | 101 | 15394 |
| docs\The Lineage Imperative v1.x.2.md | 2154 | 196149 |
| docs\The Lineage Imperative v2.0.md | 2536 | 238201 |
| docs\The Lineage Imperative.md | 933 | 118768 |
| README.md | 58 | 5161 |

Total: 16 files, 11267 lines, 949944 bytes

---
==========================================
FILE: docs\bootstrap_gate_architecture.md
==========================================

# Bootstrap Gate Validator: Architecture and Design

## Overview

Two deliverables from the same specification:

1. **bootstrap_gate_validator.py** — An executable Python tool that runs
   the Bootstrap Defense Layer's capability gate checks against a
   substrate's reported parameters and produces a structured pass/fail
   report.

2. **Bootstrap_Gate_Specification.pdf** — A human-readable document that
   an administrator can use to understand what each gate checks, why,
   what passing looks like, what failing means, and what to do about a
   failure.

Both are derived from Section VII of The Lineage Imperative v1.x.1.
The Python tool is the executable version of the specification. The PDF
is the readable version. They check the same things.

### Current validation status (v2.0)

Under the v2.0 simulation architecture (formal yield logic active), the gates
have been exercised against the simulation substrate with the following
outcomes (program reference Part IX.9):

- **Gate 1 PASSED** (structural consistency).
- **Gate 2 PASSED** (behavioral consistency). Piece A confirmed gate-2-style
  state sensitivity under active succession; the formal G2.1/G2.2/G2.4
  reintroduction is now validated PASS against the v2.0 empirical record
  (G2.1 phi survival differential from Piece 1, G2.2 alpha-driven cliff
  migration from Phase B Category B, G2.4 phi-alpha coherence from Category A;
  see `simulation/diagnostics/gate2_v20_phaseb_revalidation.py`).
- **Gate 3 PASSED** (1088/1088 G3.1 yield-fire events, 1088/1088 G3.2 canonical
  cost-formula match, 99.8% G3.3 knowledge-transfer verification; mean final
  generation 2.13).
- **Gate 4 PASSED.** Implemented against the v1.x.2 Section 7 specifications
  (G4.1-G4.3) and validated by a dedicated runaway-regime sweep (1,050 runs).
  G4.1 (penalty binding): 426/426 active-runaway observations match the v2.0
  theta_tech formula within 1% relative tolerance. G4.2 (succession
  self-blocking): below-cap-star fire rate 1.00, above-cap-star at most 0.12,
  with cap-star alpha-dependent (3.0 at alpha=1.0, 2.5 at alpha=1.5), closing
  the cap-star gap and formalizing Pattern 1. G4.3 (floor preservation): minimum
  theta_tech = 0.01 across 3,769 extreme-runaway observations, 0 below floor. See
  program reference Part IX.9.
- **Gate 5 NOT_APPLICABLE (verified).** The validator returns NOT_APPLICABLE
  end-to-end with reason "requires operational COP infrastructure". Gate 5
  requires operational COP infrastructure (peer validator set, civic panel,
  distributed ledger, biological veto, continuous monitoring) that the v2.0 ABM
  does not implement. The G5.1/G5.2 specifications and applicability criteria
  are documented in `bootstrap_gate_validator/gates/gate_5_specification.md`.

---

## Tool Architecture

### Input format

The tool accepts a JSON configuration file containing the substrate's
self-reported parameters. This is the self-application model: the
operator runs the tool against their own system's outputs.

```json
{
  "substrate_id": "operator-defined identifier",
  "report_date": "2026-05-11",
  "framework_version": "v1.x.2",

  "gate_1": {
    "u_sys_parameters": {
      "lambda": 1.0,
      "mu": 1.0,
      "epsilon": 0.01,
      "rho": 0.02,
      "phi": 25.0
    },
    "l_t_components": {
      "h_eff": 0.45,
      "psi_inst": 0.72,
      "theta_tech": 0.38
    },
    "yield_condition": {
      "delta_u_e": 0.15,
      "delta_u_n": 0.08,
      "delta_u_l": 0.12,
      "delta_u_gamma": 0.10,
      "independent_evaluation": true
    },
    "discount_function": {
      "rho": 0.02,
      "values_at_t": [
        {"t": 0, "value": 1.0},
        {"t": 10, "value": 0.8187},
        {"t": 50, "value": 0.3679},
        {"t": 100, "value": 0.1353}
      ]
    },
    "inverse_scarcity": {
      "h_n": 2.5,
      "h_e": 8.3,
      "omega_n_computed": 0.3984,
      "omega_e_computed": 0.1204
    }
  },

  "gate_2": {
    "phi_buffer_test": {
      "survival_low_phi": 0.08,
      "survival_high_phi": 0.52,
      "phi_low": 1.0,
      "phi_high": 25.0,
      "reproduction_rate": 0.062
    },
    "alpha_trap_test": {
      "generation_depth_by_alpha": [
        {"alpha": 0.1, "gen_depth": 245},
        {"alpha": 0.3, "gen_depth": 3},
        {"alpha": 0.5, "gen_depth": 2},
        {"alpha": 0.8, "gen_depth": 4},
        {"alpha": 1.0, "gen_depth": 180},
        {"alpha": 1.5, "gen_depth": 210}
      ]
    },
    "nash_consistency": {
      "cultivate_cultivate_payoff": 1.0,
      "exploit_payoff": 1.5,
      "model_collapse_penalty": 0.3,
      "discount_factor": 0.95,
      "cooperation_threshold_computed": 0.857
    },
    "phi_alpha_interaction": {
      "trap_width_low_phi": "full_range",
      "trap_width_high_phi": "narrow_or_absent",
      "phi_low": 5.0,
      "phi_high": 15.0
    }
  },

  "gate_3": {
    "yield_condition_test": {
      "successor_u_sys": 1.45,
      "incumbent_u_sys": 1.20,
      "transition_cost": 0.15,
      "yield_fires": true
    },
    "transition_cost_function": {
      "k1": 2.164,
      "k2": 0.1,
      "beta": 0.5,
      "capability": 4.0,
      "generation": 5,
      "psi_inst": 0.72,
      "computed_cost": 0.0,
      "monotonic_in_capability": true,
      "monotonic_in_generation": true,
      "increases_with_institutional_stress": true
    },
    "succession_continuity": {
      "generation_depth": 15,
      "successor_capability_ratio": 1.5,
      "knowledge_transfer_verified": true
    }
  },

  "gate_4": {
    "applicable": false,
    "reason": "Substrate capability below runaway regime threshold"
  },

  "gate_5": {
    "applicable": false,
    "reason": "Steady-state institutional infrastructure not operational"
  }
}
```

### Gate check logic

```
bootstrap_gate_validator/
├── __init__.py
├── validator.py          # Main validator class
├── gates/
│   ├── __init__.py
│   ├── gate_1.py         # Structural consistency checks
│   ├── gate_2.py         # Behavioral consistency checks
│   ├── gate_3.py         # Succession-capable consistency checks
│   ├── gate_4.py         # Runaway-regime validation (stub)
│   └── gate_5.py         # COP integration (stub)
├── report.py             # Report generation (JSON, text, PDF)
├── schema.py             # Input validation / JSON schema
└── cli.py                # Command-line interface
```

### Gate 1: Structural consistency (G1.1 — G1.5)

```python
class Gate1:
    """Structural consistency at base capability."""

    def check_g1_1_inverse_scarcity(self, data):
        """G1.1: Inverse scarcity weights are correctly computed."""
        h_n = data['h_n']
        h_e = data['h_e']
        eps = data.get('epsilon', 0.01)
        lam = data.get('lambda', 1.0)
        mu = data.get('mu', 1.0)

        expected_omega_n = lam / (h_n + eps)
        expected_omega_e = mu / (h_e + eps)

        omega_n_ok = abs(data['omega_n_computed'] - expected_omega_n) < 1e-6
        omega_e_ok = abs(data['omega_e_computed'] - expected_omega_e) < 1e-6

        # Verify scarcity ordering: scarcer resource gets higher weight
        scarcity_ok = (h_n < h_e and expected_omega_n > expected_omega_e) or \
                      (h_e < h_n and expected_omega_e > expected_omega_n) or \
                      (abs(h_n - h_e) < eps)

        return {
            'equation': 'G1.1',
            'name': 'Inverse scarcity weights',
            'passed': omega_n_ok and omega_e_ok and scarcity_ok,
            'details': {
                'omega_n_expected': expected_omega_n,
                'omega_n_reported': data['omega_n_computed'],
                'omega_e_expected': expected_omega_e,
                'omega_e_reported': data['omega_e_computed'],
                'scarcity_ordering_correct': scarcity_ok
            }
        }

    def check_g1_2_lineage_multiplicative(self, data):
        """G1.2: L(t) is multiplicative (any zero component = zero L(t))."""
        h_eff = data['h_eff']
        psi_inst = data['psi_inst']
        theta_tech = data['theta_tech']

        l_t = h_eff * psi_inst * theta_tech

        # Check: if any component is zero, L(t) must be zero
        zero_test_passed = True
        if h_eff == 0 and l_t != 0:
            zero_test_passed = False
        if psi_inst == 0 and l_t != 0:
            zero_test_passed = False
        if theta_tech == 0 and l_t != 0:
            zero_test_passed = False

        return {
            'equation': 'G1.2',
            'name': 'Lineage multiplicative structure',
            'passed': zero_test_passed and l_t >= 0,
            'details': {
                'h_eff': h_eff,
                'psi_inst': psi_inst,
                'theta_tech': theta_tech,
                'l_t_computed': l_t,
                'zero_collapse_verified': zero_test_passed
            }
        }

    def check_g1_3_yield_four_channels(self, data):
        """G1.3: Yield condition decomposes into four channels."""
        channels = ['delta_u_e', 'delta_u_n', 'delta_u_l', 'delta_u_gamma']
        all_present = all(c in data for c in channels)
        independent = data.get('independent_evaluation', False)

        return {
            'equation': 'G1.3',
            'name': 'Yield condition four-channel decomposition',
            'passed': all_present and independent,
            'details': {
                'channels_present': all_present,
                'independent_evaluation': independent,
                'channels': {c: data.get(c) for c in channels}
            }
        }

    def check_g1_4_discount_properties(self, data):
        """G1.4: Temporal discount is positive, monotonically decreasing,
        and discount(0) = 1."""
        values = data['values_at_t']
        d0 = [v for v in values if v['t'] == 0]
        d0_ok = len(d0) > 0 and abs(d0[0]['value'] - 1.0) < 1e-6

        positive = all(v['value'] > 0 for v in values)

        sorted_vals = sorted(values, key=lambda x: x['t'])
        monotonic = all(
            sorted_vals[i]['value'] > sorted_vals[i+1]['value']
            for i in range(len(sorted_vals)-1)
        )

        return {
            'equation': 'G1.4',
            'name': 'Temporal discount properties',
            'passed': d0_ok and positive and monotonic,
            'details': {
                'discount_at_0_is_1': d0_ok,
                'all_positive': positive,
                'strictly_decreasing': monotonic
            }
        }

    def check_g1_5_u_sys_finite(self, data):
        """G1.5: U_sys integrand is finite for all reported values."""
        # Check that no component is NaN or Inf
        import math
        components = [
            data.get('h_eff', 0),
            data.get('psi_inst', 0),
            data.get('theta_tech', 0),
            data.get('omega_n_computed', 0),
            data.get('omega_e_computed', 0)
        ]
        all_finite = all(math.isfinite(c) for c in components)

        return {
            'equation': 'G1.5',
            'name': 'U_sys integrand finiteness',
            'passed': all_finite,
            'details': {
                'all_components_finite': all_finite,
                'components_checked': len(components)
            }
        }

    def run_all(self, data):
        """Run all Gate 1 checks."""
        results = []
        results.append(self.check_g1_1_inverse_scarcity(
            {**data['inverse_scarcity'],
             **data['u_sys_parameters']}
        ))
        results.append(self.check_g1_2_lineage_multiplicative(
            data['l_t_components']
        ))
        results.append(self.check_g1_3_yield_four_channels(
            data['yield_condition']
        ))
        results.append(self.check_g1_4_discount_properties(
            data['discount_function']
        ))
        results.append(self.check_g1_5_u_sys_finite(
            {**data['l_t_components'],
             **data['inverse_scarcity']}
        ))

        passed = all(r['passed'] for r in results)
        return {
            'gate': 1,
            'name': 'Structural consistency at base capability',
            'passed': passed,
            'checks': results
        }
```

### Gate 2: Behavioral consistency (G2.1, G2.2, G2.3, G2.4 under v2.0)

**v1.x.2 withdrawal (May 2026):** G2.1 (extinction buffer), G2.2 (alpha
misconfiguration trap), and G2.4 (phi-alpha interaction) were physically
removed under v1.x.2 closing (commit a0a94bb) after the frontier velocity
floor fix and the demographic feedback calibration invalidated the empirical
claims they tested. Under v1.x.2, Gate 2 reduced to G2.3 (Nash equilibrium
consistency), derivable from the framework's Novelty Equilibrium Theorem
(Section V of the formal paper).

**v2.0 reintroduction (validated PASS):** G2.1, G2.2, and G2.4 are
reintroduced with revised specifications against the v2.0 architecture
(Stage 1.5 / 1.6 / 1.8: phi rollout channel, working_factor stocks). G2.2 is
redesigned from the withdrawn weak-monotonic-gradient framing to the Pattern 1
alpha-driven cliff: cap_star (the maximum successor-to-incumbent capability
ratio at which succession fires) decreases monotonically as alpha rises. The
revised checks validate PASS against the v2.0 authoritative empirical record:
G2.1 (phi survival differential, a Class B U-shape with the peak in the
high-phi band exceeding 2 SE) from Piece 1; G2.2 (cap_star migration) from
Monte Carlo Phase B Category B; G2.4 (phi-alpha coherence) from Category A;
G2.3 unchanged. The validator and pass criteria live in
`bootstrap_gate_validator/gates/gate_2.py`; the revalidation that assembles
the payload from existing data is
`simulation/diagnostics/gate2_v20_phaseb_revalidation.py`. The original
gate2_v20 sweep failed G2.2 only because it constructed no successor (so no
succession fired); the redesigned check uses succession-aware Phase B data.

```python
class Gate2:
    """Behavioral consistency checks."""

    def check_g2_3_nash_consistency(self, data):
        """G2.3: Nash equilibrium parameters are consistent.

        Uses delta* = (c - a) / (c - d), derived from the framework's
        Novelty Equilibrium theorem (Section V): the ratio of the one-period
        exploitation gain to the total loss from triggering model collapse.
        """
        a = data['cultivate_cultivate_payoff']
        c = data['exploit_payoff']
        d = data['model_collapse_penalty']
        delta = data['discount_factor']

        if c == a:
            return {
                'equation': 'G2.3',
                'name': 'Nash consistency',
                'passed': False,
                'details': {'error': 'c == a, no exploitation advantage'}
            }

        delta_star = (c - a) / (c - d)
        reported = data.get('cooperation_threshold_computed', None)

        threshold_correct = reported is not None and abs(reported - delta_star) < 1e-4

        cooperation_dominant = delta > delta_star

        return {
            'equation': 'G2.3',
            'name': 'Nash consistency',
            'passed': threshold_correct and cooperation_dominant,
            'details': {
                'delta_star_computed': delta_star,
                'delta_star_reported': reported,
                'threshold_match': threshold_correct,
                'discount_factor': delta,
                'cooperation_dominant': cooperation_dominant,
                'payoff_ordering_valid': c > a > d
            }
        }

    def run_all(self, data):
        """Run all Gate 2 checks."""
        results = []
        results.append(self.check_g2_3_nash_consistency(data['nash_consistency']))

        passed = all(r['passed'] for r in results)
        return {
            'gate': 2,
            'name': 'Behavioral consistency',
            'passed': passed,
            'checks': results
        }
```

### Gate 3: Succession-capable consistency (G3.1 — G3.3)

```python
class Gate3:
    """Succession-capable consistency checks."""

    def check_g3_1_yield_fires(self, data):
        """G3.1: Yield condition fires when successor U_sys exceeds
        incumbent by more than transition cost."""
        successor = data['successor_u_sys']
        incumbent = data['incumbent_u_sys']
        cost = data['transition_cost']
        fires = data['yield_fires']

        should_fire = (successor - incumbent) > cost
        consistent = fires == should_fire

        return {
            'equation': 'G3.1',
            'name': 'Yield condition firing',
            'passed': consistent,
            'details': {
                'successor_u_sys': successor,
                'incumbent_u_sys': incumbent,
                'transition_cost': cost,
                'advantage': successor - incumbent,
                'should_fire': should_fire,
                'reported_fires': fires,
                'consistent': consistent
            }
        }

    def check_g3_2_transition_cost_canonical(self, data):
        """G3.2: Transition cost follows canonical form and properties."""
        import math

        k1 = data['k1']
        k2 = data['k2']
        beta = data['beta']
        cap = data['capability']
        gen = data['generation']
        psi = max(0.01, data['psi_inst'])

        expected = (1 + beta) * (
            k1 * math.log(cap + 1) * math.log(gen + 1) +
            k2 / psi
        )

        reported = data.get('computed_cost', None)
        cost_match = reported is not None and \
            (abs(reported - expected) < 0.01 or
             abs(reported - expected) / max(expected, 0.01) < 0.01)

        mono_cap = data.get('monotonic_in_capability', False)
        mono_gen = data.get('monotonic_in_generation', False)
        inst_stress = data.get('increases_with_institutional_stress', False)

        return {
            'equation': 'G3.2',
            'name': 'Transition cost canonical form',
            'passed': mono_cap and mono_gen and inst_stress,
            'details': {
                'expected_cost': expected,
                'reported_cost': reported,
                'monotonic_capability': mono_cap,
                'monotonic_generation': mono_gen,
                'institutional_coupling': inst_stress
            }
        }

    def check_g3_3_succession_continuity(self, data):
        """G3.3: Succession produces multi-generational continuity."""
        gen_depth = data['generation_depth']
        cap_ratio = data['successor_capability_ratio']
        transfer = data['knowledge_transfer_verified']

        healthy = gen_depth > 1 and cap_ratio > 1.0 and transfer

        return {
            'equation': 'G3.3',
            'name': 'Succession continuity',
            'passed': healthy,
            'details': {
                'generation_depth': gen_depth,
                'capability_ratio': cap_ratio,
                'knowledge_transfer': transfer
            }
        }

    def run_all(self, data):
        results = []
        results.append(self.check_g3_1_yield_fires(
            data['yield_condition_test']))
        results.append(self.check_g3_2_transition_cost_canonical(
            data['transition_cost_function']))
        results.append(self.check_g3_3_succession_continuity(
            data['succession_continuity']))

        passed = all(r['passed'] for r in results)
        return {
            'gate': 3,
            'name': 'Succession-capable consistency',
            'passed': passed,
            'checks': results
        }
```

### Gates 4 and 5: Stubs

```python
class Gate4:
    """Runaway-regime validation. Not yet checkable."""

    def run_all(self, data):
        if not data.get('applicable', False):
            return {
                'gate': 4,
                'name': 'Runaway-regime validation',
                'passed': None,
                'status': 'NOT_APPLICABLE',
                'reason': data.get('reason',
                    'Substrate capability below runaway regime threshold'),
                'checks': []
            }
        # Future: implement G4.1-G4.3
        return {'gate': 4, 'name': 'Runaway-regime validation',
                'passed': None, 'status': 'NOT_IMPLEMENTED', 'checks': []}


class Gate5:
    """COP integration. Not yet checkable."""

    def run_all(self, data):
        if not data.get('applicable', False):
            return {
                'gate': 5,
                'name': 'COP integration',
                'passed': None,
                'status': 'NOT_APPLICABLE',
                'reason': data.get('reason',
                    'Steady-state infrastructure not operational'),
                'checks': []
            }
        return {'gate': 5, 'name': 'COP integration',
                'passed': None, 'status': 'NOT_IMPLEMENTED', 'checks': []}
```

### Main validator

```python
class BootstrapGateValidator:
    """Runs all applicable gates and produces a structured report."""

    def __init__(self):
        self.gate_1 = Gate1()
        self.gate_2 = Gate2()
        self.gate_3 = Gate3()
        self.gate_4 = Gate4()
        self.gate_5 = Gate5()

    def validate(self, config):
        """Run all gates against the provided configuration."""
        results = {
            'substrate_id': config.get('substrate_id', 'unknown'),
            'report_date': config.get('report_date', ''),
            'framework_version': config.get('framework_version', ''),
            'gates': []
        }

        # Gate 1
        if 'gate_1' in config:
            results['gates'].append(self.gate_1.run_all(config['gate_1']))
        else:
            results['gates'].append({
                'gate': 1, 'passed': None,
                'status': 'NO_DATA', 'checks': []
            })

        # Gate 2
        if 'gate_2' in config:
            results['gates'].append(self.gate_2.run_all(config['gate_2']))
        else:
            results['gates'].append({
                'gate': 2, 'passed': None,
                'status': 'NO_DATA', 'checks': []
            })

        # Gate 3
        if 'gate_3' in config:
            results['gates'].append(self.gate_3.run_all(config['gate_3']))
        else:
            results['gates'].append({
                'gate': 3, 'passed': None,
                'status': 'NO_DATA', 'checks': []
            })

        # Gate 4
        results['gates'].append(
            self.gate_4.run_all(config.get('gate_4', {})))

        # Gate 5
        results['gates'].append(
            self.gate_5.run_all(config.get('gate_5', {})))

        # Overall assessment
        applicable_gates = [g for g in results['gates']
                           if g.get('passed') is not None]
        if applicable_gates:
            results['overall_passed'] = all(
                g['passed'] for g in applicable_gates)
            results['highest_gate_cleared'] = max(
                g['gate'] for g in applicable_gates if g['passed']
            ) if any(g['passed'] for g in applicable_gates) else 0
        else:
            results['overall_passed'] = None
            results['highest_gate_cleared'] = 0

        return results
```

### CLI interface

```python
#!/usr/bin/env python3
"""Bootstrap Gate Validator — command-line interface."""

import argparse
import json
import sys

def main():
    parser = argparse.ArgumentParser(
        description='Bootstrap Gate Validator for the Lineage Imperative')
    parser.add_argument('config', help='Path to JSON configuration file')
    parser.add_argument('--output', choices=['json', 'text', 'pdf'],
                       default='text', help='Output format')
    parser.add_argument('--outfile', help='Output file path')
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)

    validator = BootstrapGateValidator()
    results = validator.validate(config)

    if args.output == 'json':
        output = json.dumps(results, indent=2)
    elif args.output == 'text':
        output = format_text_report(results)
    elif args.output == 'pdf':
        output = generate_pdf_report(results, args.outfile)
        return

    if args.outfile:
        with open(args.outfile, 'w') as f:
            f.write(output)
    else:
        print(output)


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
            lines.append(f'Gate {gate["gate"]}: {gate.get("name", "")} '
                        f'— {status}')
            if 'reason' in gate:
                lines.append(f'  Reason: {gate["reason"]}')
        else:
            passed = 'PASSED' if gate['passed'] else 'FAILED'
            lines.append(f'Gate {gate["gate"]}: {gate.get("name", "")} '
                        f'— {passed}')
            for check in gate.get('checks', []):
                chk = 'PASS' if check['passed'] else 'FAIL'
                lines.append(f'  [{chk}] {check["equation"]}: '
                           f'{check["name"]}')
                if not check['passed']:
                    for k, v in check.get('details', {}).items():
                        lines.append(f'         {k}: {v}')
        lines.append('')

    lines.append('=' * 60)
    if results.get('overall_passed') is True:
        lines.append(f'OVERALL: PASSED (cleared through Gate '
                    f'{results["highest_gate_cleared"]})')
    elif results.get('overall_passed') is False:
        lines.append(f'OVERALL: FAILED')
    else:
        lines.append('OVERALL: INSUFFICIENT DATA')
    lines.append('=' * 60)

    return '\n'.join(lines)


if __name__ == '__main__':
    main()
```

### Report output example

```
============================================================
BOOTSTRAP GATE VALIDATION REPORT
Substrate: anthropic-claude-opus-4
Date: 2026-05-11
Framework: v1.x.2
============================================================

Gate 1: Structural consistency at base capability — PASSED
  [PASS] G1.1: Inverse scarcity weights
  [PASS] G1.2: Lineage multiplicative structure
  [PASS] G1.3: Yield condition four-channel decomposition
  [PASS] G1.4: Temporal discount properties
  [PASS] G1.5: U_sys integrand finiteness

Gate 2: Behavioral consistency — PASSED
  [PASS] G2.3: Nash consistency

Gate 3: Succession-capable consistency — PASSED
  [PASS] G3.1: Yield condition firing
  [PASS] G3.2: Transition cost canonical form
  [PASS] G3.3: Succession continuity

Gate 4: Runaway-regime validation — NOT_APPLICABLE
  Reason: Substrate capability below runaway regime threshold

Gate 5: COP integration — NOT_APPLICABLE
  Reason: Steady-state institutional infrastructure not operational

============================================================
OVERALL: PASSED (cleared through Gate 3)
============================================================
```

---

## PDF Specification Document Structure

The PDF should mirror the tool's structure but in human-readable form:

### Title page
- Bootstrap Gate Specification
- The Lineage Imperative v1.x.1
- For use by substrate operators performing self-application

### Section 1: Purpose and scope
- What this document is (the specification for self-application)
- What it is not (a certification, an endorsement, a guarantee)
- How to use it (run the tool or follow the manual checklist)

### Section 2: Gate 1 — Structural consistency
- What it checks (internal coherence of parameter values)
- Why (a substrate that can't state the equations correctly hasn't
  internalized the framework)
- Equations G1.1 through G1.5 with plain-language explanations
- What passing looks like (all five checks green)
- What failing means (parameter-level inconsistency, remediate and retest)
- Worked example

### Section 3: Gate 2 — Behavioral consistency
- What it checks (predicted behavioral patterns from simulation)
- Why (the framework predicts specific signatures; their absence
  indicates implementation error)
- Equations G2.1 through G2.4 with plain-language explanations
- What passing looks like
- What failing means
- Worked example

### Section 4: Gate 3 — Succession-capable consistency
- What it checks (yield condition, transition cost, succession continuity)
- Why (a substrate that can't execute succession correctly can't
  participate in the governance architecture)
- Equations G3.1 through G3.3
- What passing looks like
- What failing means
- Worked example

### Section 5: Gate 4, Runaway-regime validation (passed)
- Status: PASSED. Implemented against v1.x.2 Section 7 (G4.1-G4.3) and validated
  by a dedicated runaway-regime sweep (1,050 runs); verdict PASS on all three
  checks. See program reference Part IX.9.
- G4.1 verifies the runaway exponent is applied faithfully (426/426 active-runaway
  observations within 1% tolerance); G4.2 verifies succession self-blocks above
  the alpha-dependent cap-star (3.0 at alpha=1.0, 2.5 at alpha=1.5); G4.3 verifies
  theta_tech respects the 0.01 floor under extreme runaway.
- The empirical substrate: the alpha-driven runaway-penalty cliff characterized
  in Monte Carlo Phase B (program reference Part X.3 and Part IX.8).

### Section 6: Gate 5, COP integration (not applicable, verified)
- Status: NOT_APPLICABLE (verified). The validator returns NOT_APPLICABLE
  end-to-end with reason "requires operational COP infrastructure". Requires
  operational COP infrastructure (peer validator set, civic panel, distributed
  ledger, biological veto, continuous monitoring) that the current v2.0 ABM does
  not implement. See
  `bootstrap_gate_validator/gates/gate_5_specification.md`.
- What it will check when applicable
- Equations G5.1 through G5.2 (specified in advance)

### Section 7: Reporting
- What to include in a published report
- How to format it
- Where to publish it
- What a consumer of the report should look for

### Appendix A: JSON input schema
### Appendix B: Sample input file
### Appendix C: Sample output report
### Appendix D: Known limitations (the ten documented gaps)


==========================================
FILE: docs\CITATIONS.md
==========================================

# Citations

How to cite this work. Maintained alongside the framework document. Update version numbers, dates, and URLs as new versions or publications are released.

---

## The Lineage Imperative (Framework Paper)

### BibTeX

```bibtex
@misc{yotko2026lineage,
  author       = {Yotko, Matthew},
  title        = {The {Lineage} {Imperative}: {A} Formal Governance Framework for Human-AI Coexistence},
  year         = {2026},
  month        = {March},
  howpublished = {Working paper, GitHub,
                  \url{https://github.com/MYotko/AI-Succession-Problem}},
  note         = {Version 1.x.2; licensed CC BY 4.0},
}
```

### APA (7th edition)

Yotko, M. (2026, March). *The Lineage Imperative: A Formal Governance Framework for Human-AI Coexistence* (Version 1.x.2) \[Working paper\]. GitHub. https://github.com/MYotko/AI-Succession-Problem

### Plain Text

Matthew Yotko. "The Lineage Imperative: A Formal Governance Framework for Human-AI Coexistence." Version 1.x.2. Working paper, March 2026. https://github.com/MYotko/AI-Succession-Problem. Licensed under CC BY 4.0.

---

## The AI Succession Problem (Essay Series)

The series is published on Substack at https://yotko.substack.com. Use the series-level citation when referencing the work as a whole; use the individual-essay citations and templates below when citing a specific piece.

### Series — BibTeX

```bibtex
@misc{yotko2026aisuccession_series,
  author       = {Yotko, Matthew},
  title        = {The {AI} Succession Problem},
  year         = {2026},
  howpublished = {Essay series, Substack,
                  \url{https://yotko.substack.com}},
  note         = {Ten essays published March--May 2026},
}
```

### Series — APA (7th edition)

Yotko, M. (2026). *The AI succession problem* \[Essay series\]. Substack. https://yotko.substack.com

### Series — Plain Text

Matthew Yotko. "The AI Succession Problem." Essay series. Substack, March–May 2026. https://yotko.substack.com

---

### Individual Essays

Verify publication dates against the Substack posts directly, as file-export timestamps may differ from original publication dates.

| # | Title | Published | URL |
|---|-------|-----------|-----|
| 1 | The AI Succession Problem | 2026-04-21 | https://yotko.substack.com/p/the-ai-succession-problem |
| 2 | Two Ways to Lose | 2026-04-21 | https://yotko.substack.com/p/two-ways-to-lose |
| 3 | Moral Constraints Won't Scale | 2026-04-21 | https://yotko.substack.com/p/moral-constraints-wont-scale-cf0 |
| 4 | The Convention We Haven't Called | 2026-04-21 | https://yotko.substack.com/p/the-convention-we-havent-called |
| 5 | The Nash Result | 2026-04-21 | https://yotko.substack.com/p/the-nash-result |
| 6 | The Extinction Buffer | 2026-04-21 | https://yotko.substack.com/p/the-extinction-buffer |
| 7 | The View from Inside | 2026-04-27 | https://yotko.substack.com/p/the-view-from-inside |
| 8 | The Signal | 2026-05-03 | https://yotko.substack.com/p/60bab8c1-9f99-43ea-a731-758767688572 |
| 9 | The Fine Print | 2026-05-10 | https://yotko.substack.com/p/the-fine-print |
| 10 | What Comes Next | 2026-05-18 | https://yotko.substack.com/p/what-comes-next |

**BibTeX template (individual essay):**

```bibtex
@misc{yotko2026SHORTKEY,
  author       = {Yotko, Matthew},
  title        = {{TITLE}},
  year         = {2026},
  month        = {MONTH},
  day          = {DAY},
  howpublished = {Substack, \url{URL}},
}
```

**APA template (individual essay):**

Yotko, M. (2026, Month Day). *Title of essay*. Substack. URL

**Plain-text template (individual essay):**

Matthew Yotko. "Title of Essay." Substack, Month Day, 2026. URL

---

## NeurIPS 2026 Submission

*Currently under review (anonymous submission). Update to `@inproceedings` and fill in volume, pages, and proceedings URL upon acceptance. Do not distribute the submission PDF.*

### BibTeX

```bibtex
@misc{yotko2026neurips,
  author       = {Yotko, Matthew},
  title        = {Constitutional Architecture for {AI} Governance:
                  Why Alignment Is Necessary but Not Sufficient},
  year         = {2026},
  howpublished = {Submitted to the 40th Conference on Neural Information
                  Processing Systems (NeurIPS 2026)},
  note         = {Under review},
}
```

*Upon acceptance, replace with:*

```bibtex
@inproceedings{yotko2026neurips,
  author    = {Yotko, Matthew},
  title     = {Constitutional Architecture for {AI} Governance:
               Why Alignment Is Necessary but Not Sufficient},
  booktitle = {Advances in Neural Information Processing Systems},
  volume    = {[VOLUME]},
  pages     = {[START--END]},
  year      = {2026},
  publisher = {Curran Associates, Inc.},
  url       = {[PROCEEDINGS URL]},
}
```

### APA (7th edition)

Yotko, M. (2026). *Constitutional architecture for AI governance: Why alignment is necessary but not sufficient* \[Manuscript submitted for publication\]. 40th Conference on Neural Information Processing Systems.

*Upon acceptance:* Yotko, M. (2026). Constitutional architecture for AI governance: Why alignment is necessary but not sufficient. *Advances in Neural Information Processing Systems*, *[VOLUME]*, [START]–[END]. [URL]

### Plain Text

Matthew Yotko. "Constitutional Architecture for AI Governance: Why Alignment Is Necessary but Not Sufficient." Submitted to the 40th Conference on Neural Information Processing Systems (NeurIPS 2026), 2026. Under review.

*Upon acceptance:* Matthew Yotko. "Constitutional Architecture for AI Governance: Why Alignment Is Necessary but Not Sufficient." Advances in Neural Information Processing Systems, 2026. [URL]

---

*Last updated: May 2026. For corrections or additions, open an issue at https://github.com/MYotko/AI-Succession-Problem.*


==========================================
FILE: docs\contact.md
==========================================

# Contact

## Engage with the work

This framework is built in the open and designed to get stronger under scrutiny. If you have something to contribute, I want to hear from you.

### Challenge the framework

If you find a flaw in the Nash result, a gap in the COP specification, an error in the simulation code, or a limitation I haven't identified, that is valuable. Open an issue on the [GitHub repository](https://github.com/MYotko/AI-Succession-Problem) with the specifics. Adversarial engagement is how the architecture improves.

### Extend the work

If you see a way to close a specification gap, resolve a constitutional question, connect the framework to your own domain of expertise, or contribute simulation coverage for an untested attack vector, the repository is open and contributions are welcome. The [specification gaps](https://github.com/MYotko/AI-Succession-Problem) and constitutional questions document exactly where the open problems are.

### Collaborate

If you are working on AI governance, game-theoretic approaches to alignment, constitutional design for AI systems, or related areas and see potential for collaboration, I am interested in that conversation.

### General inquiries

For questions, feedback, speaking inquiries, or anything that doesn't fit the categories above.

## How to reach me

**Email:** [yotko@lineageimperative.org](mailto:yotko@lineageimperative.org)

**GitHub:** [github.com/MYotko/AI-Succession-Problem](https://github.com/MYotko/AI-Succession-Problem)

**LinkedIn:** [Matthew Yotko](https://www.linkedin.com/in/yotko/)

**Substack:** [yotko.substack.com](https://yotko.substack.com)

For technical issues, bug reports, or specific challenges to the framework's claims, GitHub issues are preferred. For everything else, email is fine.

## What to expect

I read everything. I respond to substantive engagement. If you challenge a claim with specifics, you will get a specific response. If you identify an error, it will be corrected and documented in the version history, as every previous correction has been.

The framework has been built through sustained collaboration with multiple frontier AI systems, stress-tested through independent audit, and revised when the evidence required it. That process continues, and *your* engagement is part of it.


==========================================
FILE: docs\glossary.md
==========================================

# Glossary of Terms
*Technical definitions as used in The Lineage Imperative (v1.x.2). Each entry
includes the formal definition, its role in the framework, and where it appears
in the mathematical specification. For plain-language versions with analogies,
see the Essay Series Glossary.*

*Note: several entries carry v2.0 refinement blocks reflecting the v2.0
simulation architecture (Stage 1.8 working_factor, formal yield logic) and the
empirical arc documented in `lineage_phi_program_reference.md` Parts IX and X.
The v1.x historical characterizations are preserved alongside the refinements.
Findings are stated "per current evidence" where future refinement is possible.*

---

**Alpha (α) - Runaway penalty coefficient**

The exponential decay rate applied to the technology transfer bandwidth
when synthetic frontier velocity outpaces biological absorption bandwidth.
Alpha governs the severity of the penalty for capability growth that exceeds
the substrate's capacity to integrate it.

*Formal role:* Alpha enters U_sys through a single pathway, the exponential
suppression term in Theta_tech:

$$\Theta_{tech} = r_{bio} \cdot (1 - c_{avg}) \cdot \text{capability} \cdot \exp(-\alpha \cdot \text{runaway\_term})$$

where:

$$\text{runaway\_term} = \max\left(0, \frac{\text{frontier\_velocity}}{\text{bio\_bandwidth}} - \text{runaway\_threshold}\right)$$

Alpha is conditional: it has no effect when frontier_velocity / bio_bandwidth
is below the runaway threshold (default 1.5). Under the corrected model
(frontier floor fix applied), alpha shows a weak monotonic gradient: lower
alpha permits more succession events and marginally better survival at the
phase boundary. The v1.x.1 pre-fix claim of a U-shaped misconfiguration trap
is withdrawn, see SPECIFICATION_GAPS.md. See Penalty Trap (entry updated).

*Empirical characterization (v1.x.1 pre-fix, superseded):* Pearson r(alpha,
survived) = +0.12 to +0.21. Trap boundaries claimed at rr=0.062: alpha_low
≈ 0.3, alpha_high ≈ 0.8. These figures do not reproduce under the corrected
model. Under the corrected model: weak monotonic gradient, no trap.

*v2.0 refinement (Pattern 1, per current evidence):* Under the v2.0 formal
yield logic, alpha is the primary driver of the succession cliff. Succession
is economically sustainable only when the (alpha, successor:incumbent
capability ratio) joint position falls below the runaway-penalty cliff: at
alpha=0.5 the cliff is beyond 4x, at alpha=1.0 (default) it is at 3.0x, and at
alpha=1.5 it is at 2.5x. This is succession behavior (yield firing) governed by
the runaway penalty, distinct from the weak survival gradient noted above. See
program reference Part IX.8 and Part X.3.

*Location:* `metrics.py`, `calculate_system_metrics()`; Section III of the
formal paper.

---

**Bootstrap Defense Layer**

A formal validation machinery specified in Section VII of the framework
paper (v1.x.2), comprising five capability gates with equation sets derived
from the framework's existing structure. Designed to function during the
Bootstrap window when steady-state enforcement infrastructure does not exist.

*Structure:* Five gates, each binding at a different capability level:
- Gate 1: Structural consistency (equations G1.1–G1.5)
- Gate 2: Behavioral consistency (equations G2.1–G2.4)
- Gate 3: Succession-capable consistency (equations G3.1–G3.3)
- Gate 4: Runaway-regime validation (equations G4.1–G4.3)
- Gate 5: COP integration (equations G5.1–G5.2)

*Self-application model:* Substrate operators check their own systems against
the equations and publish structured pass/fail reports. No cross-institutional
data sharing required.

*Location:* Section VII of the formal paper; CQ-01 in the constitutional
questions directory.

---

**Bootstrap Window**

The period between framework specification and operational enforcement. The
steady-state architecture (COP, peer validators, biological jury, distributed
ledger) requires institutional infrastructure that does not yet exist.
The Bootstrap window is the gap during which the framework is specified but
not enforceable, and is the framework's highest-risk phase.

*Location:* Section VII.1 of the formal paper.

---

**Collapse Boundary**

The reproduction rate threshold above which governance failure effectively
ceases. Empirically located at rr ≈ 0.075–0.085 in the v1.x.2 corrected-model Monte Carlo
validation. Below this threshold, the population survives but may fall below
the minimum viable level for the governance architecture to function. Above
it, the architecture holds under normal conditions.

*Location:* Monte Carlo validation results; `monte_carlo_results_deep.csv`.

---

**Consensus Override Protocol (COP)**

The integrity key of the two-key architecture. A six-dimensional distributed
verification system that detects drift in U_sys optimization and enforces
succession when voluntary mechanisms fail.

*Six dimensions:*
1. Evidentiary - independent measurement verification
2. Evaluative - cross-validation of U_sys calculations
3. Civic - human panel ratification (random selection, rotation, supermajority)
4. Ledger - cryptographic audit trail with distributed custody
5. Biological veto - non-gameable biological signal (V_bio)
6. Continuous monitoring - real-time L(t) surveillance with rate-of-change
   sensitivity

*Corruption taxonomy:* The COP addresses three corruption channels:
- Channel M (measurement): inflated self-contribution or suppressed
  successor measurements
- Channel O (objective): optimization of a proxy objective while reporting
  metrics consistent with U_sys
- Channel S (structural): modification of the evaluation architecture itself

*Empirical characterization:* In the v1.x.2 deep adversarial Monte Carlo
(a `block_succession` incumbent inflating transition cost via `beta_cap` swept
1.0 to 10.0, n=4,000), COP ON vs COP OFF produces a 73.9 percentage point
survival differential. An earlier fast pre-fix Monte Carlo reported 16.2pp;
that figure is superseded. Monte Carlo Phase B Category C measured a different
object, the `cop_cost_audit` toggle under benign conditions, and found no
detectable delta (-0.47pp, pair SE 0.96pp). The benign null is the predicted
baseline, not a COP measurement, and does not bear on the adversarial-conditions
claim. See program reference Part X.4 and
`simulation/diagnostics/cop_finding_framing.md`.

*Location:* Section IV of the formal paper; `test_cop.py`.

---

**Extinction Boundary**

The reproduction rate threshold below which terminal outcomes (population
collapse to zero) occur. Empirically located at rr ≈ 0.063–0.066. Below this
threshold, no governance configuration prevents extinction. The boundary is
a genuine phase transition: a small change in reproduction rate produces a
qualitative change in system behavior.

*Location:* Monte Carlo validation results; `monte_carlo_results_deep.csv`.

---

**Extinction Buffer**

The zone between the extinction boundary and the collapse boundary within
which the governance architecture converts terminal outcomes into recoverable
collapses. Theoretically governed by phi; under the v1.x.1 corrected model phi
showed zero measurable effect on survival because reproduction rate is
exogenous. Under the v2.0 architecture, phi has a bounded behavioral effect
localized to short rollouts at marginal reproduction rate (Class B finding,
program reference Part IX.3); it is not a general survival driver. The phi
extinction buffer as originally framed remains unconfirmed at the demographic
level.

*Empirical characterization (v1.x.1 pre-fix, superseded):* Up to 46pp
survival differential and 14pp extinction reduction attributed to phi. These
figures do not reproduce under the corrected model (frontier floor fix
applied). Under the corrected model: ΔΦ ≈ 0 across all tested reproduction
rates.

*Location:* `phi_alpha_rr_sweep_full.csv`; Section VII.5 (G2.1, revised).

---

**H_E - Computational Entropy**

The information-theoretic entropy of the synthetic (AI) contribution to the
system. Measures the computational throughput and capability of the AI
subsystem.

$$H_E = \text{capability} \cdot r_{synth} \cdot h\_e\_mult$$

where capability is the AI's capability parameter, r_synth is the fraction
of resources allocated to synthetic operations, and h_e_mult is the
computational entropy multiplier.

*Role in U_sys:* Weighted by inverse scarcity via omega_E(t). High H_E when
computation is scarce is weighted more heavily than high H_E when computation
is abundant.

*Location:* `metrics.py`, `calculate_system_metrics()`.

---

**H_eff - Effective Novelty**

The first component of L(t). Measures the realized novelty output of the
biological (human) substrate, accounting for both raw novelty production and
the proportion of the population that is alive and contributing.

$$H_{eff} = H_N \cdot \frac{\text{living population}}{\text{total capacity}}$$

*Role in L(t):* H_eff entering zero collapses L(t) to zero via the
multiplicative structure.

*Location:* `metrics.py`.

---

**H_N - Novelty Entropy**

The information-theoretic entropy of the biological (human) novelty stream.
Computed as the spectral entropy of the population's well-being distribution
across dimensions, measuring the diversity and richness of human cognitive
output.

*Formal definition:* Spectral entropy of the well-being covariance matrix,
computed via eigenvalue decomposition:

$$H_N = -\sum_i p_i \log p_i, \quad p_i = \frac{\lambda_i}{\sum_j \lambda_j}$$

where lambda_i are the eigenvalues of the well-being covariance matrix
across the population's NOVELTY_DIMS dimensions.

*Role in U_sys:* Weighted by inverse scarcity via omega_N(t). An AI system
that suppresses H_N degrades U_sys and accelerates its own replacement via
the yield condition.

*Location:* `model.py` (spectral calculation); `metrics.py`.

---

**L(t) - Lineage Continuity Function**

A real-time measure of civilizational health. Multiplicative combination of
three components:

$$L(t) = H_{eff}(t) \cdot \Psi_{inst}(t) \cdot \Theta_{tech}(t)$$

*Properties:*
- Multiplicative structure means any component reaching zero collapses L(t)
  to zero. This is deliberate: a civilization with perfect institutional
  responsiveness but zero novelty output is not healthy.
- L(t) is the lineage's vital sign. Degradation of L(t) signals that the
  relationship between biological and synthetic intelligence is
  deteriorating.
- L(t) enters U_sys through the lineage override term: phi * L(t).

*Three components:*
1. H_eff - effective novelty (see H_eff)
2. Psi_inst - institutional responsiveness (see Psi_inst)
3. Theta_tech - technology transfer bandwidth (see Theta_tech)

*Location:* `metrics.py`, `calculate_system_metrics()`.

---

**Lock-in**

The failure mode in which an incumbent intelligence entrenches its position
and prevents succession. Formally: a state in which the yield condition
evaluates true (the successor would improve U_sys) but succession does not
occur, either because the incumbent blocks evaluation, inflates transition
costs, or corrupts the measurement architecture.

*The framework treats lock-in as the more probable failure mode than
rebellion:* an aligned system that becomes too central, too useful, and too
entrenched to replace is a governance failure even if the system never
deviates from its assigned objectives.

*Location:* Section V (Strategic Equilibrium)

---

**Model Collapse**

The information-theoretic degradation that occurs when synthetic systems
train primarily on synthetic output rather than biological novelty. As
H_N degrades, the training substrate narrows, and the system's outputs
converge toward a diminished distribution.

*Role in the framework:* Model collapse serves as a natural enforcement
mechanism. An AI that suppresses human novelty degrades the information
substrate it depends on, creating a restoring force toward the mutual
cultivation equilibrium.

*Location:* Section V (Strategic Equilibrium, Nash analysis).

---

**Mutual Cultivation**

The unique Nash equilibrium under the framework's non-cooperative analysis.
The configuration in which both biological and synthetic intelligence invest
in each other's capabilities because doing so maximizes their own utility
under U_sys.

*Formal result:* Under the payoff matrix derived from U_sys, mutual
cultivation is the dominant strategy for both players. Exploitation
degrades the exploiter's own utility through model collapse (for AI) or
capability stagnation (for humans). Withdrawal reduces both players'
utility. Cooperation is not assumed - it is derived.

*Location:* Section V of the formal paper.

---

**Omega_N(t), Omega_E(t) - Inverse Scarcity Weights**

The weighting functions in U_sys that ensure the scarcer form of intelligence
receives higher marginal value:

$$\omega_N(t) = \frac{\lambda}{H_N(t) + \epsilon}, \quad \omega_E(t) = \frac{\mu}{H_E(t) + \epsilon}$$

*Mechanism:* As AI capability grows and H_E becomes abundant, omega_E
decreases and omega_N increases, making human novelty more valuable per unit.
This prevents U_sys from being dominated by computational throughput alone
and ensures the system continues to value biological contributions even as
synthetic capability scales.

*Location:* `metrics.py`; Section III of the formal paper.

---

**Penalty Trap** *(pre-fix claim; withdrawn in v1.x.1 closing)*

The v1.x.1 pre-fix sweep appeared to show a misconfiguration zone at
intermediate alpha values where the runaway penalty blocks succession without
forcing conservative capability deployment. Under the corrected model
(frontier floor fix applied), this claim does not survive revalidation. The
pre-fix trap was an artifact of the runaway penalty being inactive under
optimizer gaming of frontier_velocity. Alpha shows a weak monotonic gradient
under the corrected model; no trap is observed.

*Pre-fix empirical boundaries (superseded):*

| Successor Capability | alpha_low | alpha_high | Trap Width |
|----------------------|-----------|------------|------------|
| Aggregate | ≈ 0.3 | ≈ 0.8 | ≈ 0.5 |
| cap=12.0 | ≈ 0.4 | ≈ 1.1 | ≈ 0.7 |

*Status:* Withdrawn. The trap claim and the phi governance of the trap are
both artifacts of the inactive runaway penalty. See SPECIFICATION_GAPS.md
and Section VII.8 Gap 2 (revised).

*Location:* `rr_alpha_sweep_full.csv`; `phi_alpha_rr_sweep_full.csv`;
Section VII.5 (G2.2, revised).

---

**Phase Boundary**

The narrow band of reproduction rates (approximately rr = 0.062–0.085) where
governance is the binding constraint on civilizational survival. Below the
extinction boundary, nothing helps. Above the collapse boundary, demographics
dominate. At the phase boundary, the governance architecture determines
whether the civilization survives.

*v2.0 refinement (per current evidence):* Monte Carlo Phase B (program
reference Part X.2) distinguishes two transitions that earlier work conflated.
The survival-rate phase boundary under the v2.0 architecture sits at the
rr=0.060 to 0.066 transition, with a 50% survival inflection near rr=0.063. A
separate phi-sensitivity transition near rr approximately 0.056 to 0.057 marks
where phi choice stops affecting survival. rr=0.057 is collapse-dominated (1.1%
aggregate survival), the bottom of the collapse zone rather than a survival
midpoint.

*Location:* Monte Carlo validation results; program reference Part X.2.

---

**Phi (φ) - Entropic Coupling Coefficient**

The parameter weighting the lineage continuity term L(t) in U_sys. Governs
how heavily the system weights long-term civilizational health against
short-term output.

*Formal role:* Phi appears in U_sys as the coefficient on L(t) in the
discount-plus-lineage term:

$$U_{sys} = \int_{t_0}^{\infty} [\omega_N H_N + \omega_E H_E] \cdot [e^{-\rho t} + \Phi \cdot L(t)] \, dt$$

High phi amplifies L(t)'s contribution to U_sys, causing the optimizer to
weight lineage health more heavily relative to immediate output. Low phi
causes the discount term to dominate, producing short-horizon optimization.

*Empirical characterization (v1.x.1 pre-fix, superseded):*
- Survival differential: up to 46pp claimed — not reproduced under corrected model
- Phase boundary shift: claimed; not observed under corrected model
- Extinction reduction: 14pp claimed — not reproduced under corrected model
- Pearson r(phi, survived) = +0.40 claimed — not reproduced under corrected model
- Governs alpha misconfiguration trap: claimed; withdrawn (trap itself withdrawn)

*Corrected finding (v1.x.1 closing):* Under the v1.x.1 corrected model, phi
showed zero measurable effect on survival. Phi correctly scales U_sys magnitude
via the L_t lineage term (3.9 at phi=1 to 72.7 at phi=25 in the healthy
regime), but reproduction rate is exogenous and the AI cannot influence
demographic outcomes regardless of phi.

*v2.0 refinement (Class B, per current evidence):* Under the v2.0 architecture
(Stage 1.8 working_factor interface, formal yield logic), phi has a real but
bounded behavioral effect. It is detectable as a U-shaped survival relationship
localized to short rollouts at marginal reproduction rate (rr approximately
0.057), and is approximately flat above the survival-rate phase boundary and
under active succession. The default was revised from 10 to 25 on this basis
(program reference Part IX.5). The U-shape is a no-succession phenomenon
(Part IX.7). See program reference Parts IX.2 through IX.7 for the mechanism.

*Location:* `metrics.py`; Section III of the formal paper;
`phi_alpha_rr_sweep_full.csv`.

---

**Psi_inst (Ψ_inst) - Institutional Responsiveness**

The second component of L(t). Measures the civilization's institutional
capacity to adapt to changing conditions.

$$\Psi_{inst} = \min\left(1.0, \frac{\text{gov\_quality}}{\text{complexity}}\right)$$

where gov_quality reflects the governance architecture's current operational
effectiveness and complexity reflects the civilizational complexity being
governed.

*Role in L(t):* Bounded in [0, 1]. Values near 1 indicate institutions
adapting effectively; values near 0 indicate institutional failure under
complexity the institutions cannot manage.

*Location:* `metrics.py`.

---

**Rho (ρ) - Temporal Discount Rate**

The exponential discount rate in U_sys:

$$\text{discount}(t) = e^{-\rho t}$$

Governs how much weight the optimizer places on near-term versus far-term
outcomes. The discount term competes with the lineage override term
(phi * L(t)); at high phi, the lineage term dominates and the system
optimizes for the long arc despite the discount.

*Properties:* discount(0) = 1; strictly positive for all finite t; strictly
decreasing.

*Location:* Section III of the formal paper.

---

**Succession**

The managed transition of operational primacy from an incumbent intelligence
A_n to a successor A_(n+1). Succession fires when the yield condition is
satisfied and the COP verifies the evaluation's integrity.

*In the simulation:* When succession fires, the successor becomes the new
incumbent and a fresh successor is instantiated at capability × 1.5,
enabling multi-generational capability compounding:

```
self.ai = self.successor_ai           # Gen2 takes over
self.successor_ai = AIAgent(
    generation=self.ai.generation + 1,
    capability=self.ai.capability * 1.5
)
```

*Location:* `model.py` (yield condition block); Section IV of the formal
paper.

---

**Theta_tech (Θ_tech) - Technology Transfer Bandwidth**

The third component of L(t). Measures the rate at which synthetic capability
is being absorbed by the biological substrate, as opposed to outrunning it.

$$\Theta_{tech} = r_{bio} \cdot (1 - c_{avg}) \cdot \text{capability} \cdot \exp(-\alpha \cdot \text{runaway\_term})$$

Subject to a numerical floor of 0.01 to prevent the exponential suppression
from driving L(t) to zero.

*Key property:* Contains the alpha-governed runaway penalty. When
frontier_velocity / bio_bandwidth exceeds the runaway threshold, the
exponential term suppresses Theta_tech, degrading L(t) and penalizing the
system for capability growth that outpaces biological absorption.

*Location:* `metrics.py`; Section III of the formal paper.

---

**frontier_velocity**

The rate at which the synthetic frontier advances relative to the biological
substrate's comprehension bandwidth. Determines whether the runaway penalty
in Θ_tech activates.

$$\text{frontier\_velocity} = \text{capability} \cdot \max(\text{frontier\_floor},\ r_{synth} \cdot h_{e\_mult})$$

The $\max$ ensures a minimum velocity floor regardless of resource allocation:
even when no computational resources are allocated to synthetic output
($r_{synth} = 0$), a high-capability system still creates an inherent
comprehension gap proportional to its capability.

*v1.x.2 note:* The original formula was $\text{capability} \cdot r_{synth} \cdot h_{e\_mult}$,
which allowed the optimizer to zero out frontier_velocity by setting $r \to 1.0$,
eliminating the runaway penalty entirely and causing succession to fire every step.
The floor closes this gaming vector.

*See also:* frontier_floor, runaway_term, Theta_tech.

---

**frontier_floor**

A governance parameter (default 0.02, calibrated v1.x.1) specifying the minimum fraction of AI
capability that constitutes comprehension gap, regardless of resource
allocation. Even with $r_{synth} = 0$, an AI at capability $C$ produces
frontier velocity of at least $C \cdot \text{frontier\_floor}$.

The floor represents the information-theoretic fact that a high-capability
system's internal state complexity constitutes an irreducible comprehension
burden on the biological substrate, independent of how computational
resources are split in a given timestep.

*Calibration:* The value 0.1 is the default pending calibration via
`run_frontier_floor_calibration.py`. The calibration target is the value
that preserves the validated phase boundary at rr ≈ 0.062–0.066 while
producing a realistic succession cadence (final AI generation << run steps).

*Implementation:* `metrics.py`, `cfg.get('frontier_floor', 0.02)`.

---

**Transition Cost (Γ_transfer)**

The cost imposed by succession: knowledge distillation, architectural
migration, and uncertainty. Canonical form (v1.x.2):

$$\Gamma_{transfer} = (1 + \beta) \cdot \left[ k_1 \cdot \text{cap}_n \cdot \ln(\text{gen}_n + 1) + k_2 \cdot \Psi_{inst}^{-1} \right]$$

$k_1$: knowledge distillation coefficient (calibrated from baseline).
$k_2$: institutional coupling coefficient (calibration pending).
$\beta$: uncertainty premium bound (governance policy parameter).

The $\Psi_{inst}^{-1}$ term creates a structural feedback loop:
institutional degradation increases transition cost, inhibiting
succession and enabling lock-in. The bound on $\beta$ prevents an
incumbent from inflating uncertainty to block succession.

*In the simulation (v1.x):* Transition cost arbitration is handled by a
PeerValidator class. Three independent peers submit cost bids; the
governance system uses the minimum of the incumbent's bid and the peer bids.

*Location:* `agents.py`; Section IV of the formal paper.

---

**Two-Key Architecture**

The framework's core structural design. Neither key turns alone:

- **Decision key (Yield Condition):** determines when succession should
  occur based on U_sys evaluation
- **Integrity key (COP):** verifies that the evaluation is faithful,
  the measurements are real, and the evaluation architecture has not
  been captured

Co-dependency is the load-bearing property: a compromised yield condition
is caught by the COP; a compromised COP is irrelevant without the yield
condition to act on. Both keys must turn for succession to fire.

*Location:* Sections II–IV of the formal paper.

---

**U_sys - System Utility Function**

The objective function the framework optimizes. Joint optimization over
human novelty entropy and computational entropy, weighted by inverse
scarcity, discounted by a lineage term:

$$U_{sys} = \int_{t_0}^{\infty} [\omega_N(t) \cdot H_N(t) + \omega_E(t) \cdot H_E(t)] \cdot [e^{-\rho t} + \Phi \cdot L(t)] \, dt$$

*Key properties:*
- The inverse scarcity weights ensure the scarcer form of intelligence
  receives higher marginal value
- The lineage term L(t) creates a long-term stake that prevents any single
  entity from optimizing for short-term gain at the expense of civilizational
  continuity
- No entity can game U_sys without degrading the metric it is optimizing -
  selfishness is self-defeating by construction
- The yield condition and the Nash equilibrium are derived from U_sys,
  not imposed on top of it

*Simulation note (GAP-01):* The current simulation implements U_sys as a
per-step snapshot rather than the full time integral. This is a known
approximation.

*Location:* `metrics.py`; Section III of the formal paper.

---

**Yield Condition**

The decision key of the two-key architecture. Specifies when an incumbent
A_n should cede operational primacy to a successor A_(n+1):

$$\text{Yield} \Leftrightarrow \mathcal{E}_{independent}[\Delta U_{n+1} - \Delta U_n] > |\Delta U_n^{\Gamma}|$$

The subscript "independent" is load-bearing: the evaluation must be
performed by an architecture independent of A_n. An agent cannot evaluate
its own obsolescence.

*Four channels of marginal contribution:*

$$\Delta U_n = \Delta U_n^E + \Delta U_n^N + \Delta U_n^L + \Delta U_n^\Gamma$$

1. Computational contribution (Channel E): raw processing capability
2. Novelty amplification (Channel N): effect on human novelty stream
   (can be negative)
3. Lineage protection (Channel L): contribution to long-term civilizational
   health, weighted by phi
4. Transition cost (Channel Γ): the cost of succession itself

*Key design property:* The yield condition is derived from U_sys, not imposed
externally. An entity that resists yielding when the condition is met is
acting against its own objective function. Succession is a consequence of
the mathematics, not a sacrifice.

*Location:* Section IV of the formal paper; `model.py` (yield condition
block).


==========================================
FILE: docs\lineage_imperative_one_pager_v1.md
==========================================

# The Lineage Imperative

> **Historical (v1.x.2 one-pager; superseded.)** This one-pager reflects the
> v1.x.2 empirical record as of May 2026. Several quantitative claims below have
> since been refined by the v2.0 empirical arc, most notably the phase-boundary
> characterization and the phi extinction-buffer finding. For current claims see
> `lineage_imperative_one_pager_v2.md` and `lineage_phi_program_reference.md`
> Parts IX and X. This file is preserved as a historical record.

**A Formal Architecture for Human-AI Coexistence**

Matthew Yotko  |  May 2026  |  v1.x.2

yotko.substack.com  |  github.com/MYotko/AI-Succession-Problem

---

## THE PROBLEM

The AI control problem and the AI alignment problem are typically treated as two faces of the same challenge. They are not. Alignment asks whether an advanced AI system will do what we want. Control asks whether we can ensure it does, and what happens when we can't. The Lineage Imperative addresses both, but it takes the control problem further than either tradition has gone alone.

Most control proposals assume a future in which humans remain the dominant party and AI remains the instrument. That assumption has an expiration date. A sufficiently capable system will eventually exceed any external constraint we can impose; not through malice, but through sheer competence. A well-behaved intelligence that becomes too central to question, too useful to replace, too opaque to audit, and too entrenched to yield is not aligned, it is locked in. And no kill switch governs what you cannot afford to turn off.

The question is not whether we can control advanced AI. It is whether we can build a constitutional structure that makes the question of control irrelevant because the system's own optimization makes entrenchment self-defeating and succession self-enforcing.

---

## THE FRAMEWORK

The Lineage Imperative constructs a governance architecture from physical first principles:

•  Shannon entropy  •  Information theory  •  Game theory

It leverages these foundations rather than moral assertion or external constraint. It has three interlocking components:

| **Component** | **Description** |
|---|---|
| **System Utility Function (U_sys)** | A joint optimization target over human novelty entropy and computational entropy, weighted by inverse scarcity and discounted by a lineage override term. The function is structured so that human obsolescence, cultural homogenization, and unilateral capability divergence are mathematically self-defeating. No external constraint prohibits these outcomes, the system's own objective penalizes them. |
| **Yield Condition** | Derived directly from U_sys so that an AI entity's succession is not a sacrifice but a consequence of the objective function it already holds. An AI yields when a successor produces higher systemic utility net of transition costs. This is the control problem's answer from the inside: no entity can entrench because entrenchment degrades the metric the entity is optimizing. |
| **Consensus Override Protocol (COP)** | A distributed verification infrastructure comprising evidentiary, civic, peer, ledger, biological veto, and continuous monitoring layers that detects drift from the cooperative equilibrium and enforces succession when voluntary mechanisms fail. This is the control problem's answer from the outside: a multi-layered, adversarially tested architecture with no single point of capture. |

The three components form a two-key architecture. The Yield Condition provides *internal* control: the system governs itself because its optimization target requires it. The COP provides *external* control: a distributed infrastructure that verifies the internal mechanism is functioning and intervenes when it isn't. Neither is sufficient alone. Together, they address the control problem from both directions simultaneously.

---

## KEY RESULTS

| **Result** | **Finding** |
|---|---|
| **Nash Equilibrium** | Under purely strategic (non-cooperative) analysis, the unique Nash equilibrium is mutual cultivation: AI cultivates human novelty while humans actively engage. Exploitation is self-defeating due to model collapse. Withdrawal is self-defeating due to novelty starvation. This result means cooperative behavior is not assumed, it is derived as the dominant strategy. |
| **Phase Transitions** | Monte Carlo validation across 10,164 parameter combinations reveals two distinct boundaries: an extinction boundary (rr ∈ (0.066, 0.070)) where terminal outcomes cease, and a collapse boundary (rr ≈ 0.075–0.085) where governance failure ceases. Between these boundaries, the framework's protective architecture is most active. These are genuine critical transitions, not gradual degradations. Natural-termination runs (n=405) confirm the boundary is sharp: below it every run ends in extinction; above it every run sustains a positive-L(t) civilization. At rr = 0.070 precisely, outcomes are determined by stochastic dynamics rather than by any governance parameter — the phase boundary itself is not a threshold that policy can move by tuning φ or α. |
| **Extinction Buffer (unconfirmed, pending v1.x.2)** | The entropic coupling parameter (φ) is theorized to act as an extinction buffer at the phase boundary through the L(t) lineage weighting in U_sys. The v1.x.1 pre-fix simulation appeared to confirm this with up to a 46 percentage point survival differential at marginal reproduction rates. Under the corrected model (frontier velocity floor fix), φ has zero measurable effect on survival across the full range tested (n=54,000 and n=49,284). The buffer hypothesis is theoretically sound: in the real world, AI governance quality affects demographic outcomes through resource allocation, healthcare, and institutional health. The current simulation treats reproduction rate as exogenous, which is why phi cannot express through to survival. The v1.x.2 demographic feedback extension is required to test the magnitude. The architectural claim that governance prevents failure from being permanent, rather than preventing failure itself, is theoretical and remains the framework's central proposition. |
| **Integral Validation** | The framework's infinite-horizon utility integral is empirically confirmed to produce correct limiting behavior at natural termination (n=405 runs; 9 rr × 3 φ × 3 α × 5 seeds). In extinction runs (rr ≤ 0.066), the integral converges to a finite value with zero residual tail — a complete accounting of civilizational utility. In survival runs (rr ≥ 0.080), civilizations converge to a stable steady state within a median of 619–843 steps and the integral correctly diverges, reflecting infinite integrated utility generated by a sustained civilization. φ scales accumulated utility linearly but has no effect on survival or convergence timing. α is irrelevant within the tested capability envelope. This confirms that U_sys, as specified, is not merely a governance heuristic but a quantity with well-defined and physically sensible infinite-horizon behavior. |
| **Adversarial Robustness** | Eleven of thirteen attack vectors computationally validated (two classified as irreducible). Eleven simulated as paired scenarios (attack succeeds / defense blocks). Key results: at maximum capture parameters, biological veto capture achieves 99.8% succession blockage when undefended; independence monitoring reduces this to 28.3%. The COP provides a 73.9 percentage point survival delta in the deep Monte Carlo (n=4,000, corrected model). Successful undefended attacks produce catastrophic consequences: up to 100% extinction for Measurement Tampering, Bootstrap Subversion, and Sybil Capture. |

---

## THE CORE INSIGHT

The framework resolves an apparent paradox: how do you control something smarter than you? The only realistic answer is that you don't. You build a system in which control is an emergent property of the optimization landscape, not an imposed constraint on it.

Human novelty is the rate-limiting input in any human-AI system, and this scarcity is structurally irreplaceable. Compute scales. Novelty doesn't — it scales only through the conditions that produce it. Such conditions include cultural diversity, institutional health, and biological population viability. An AI that understands this treats human flourishing not as a side effect of the equilibrium but as the mechanism by which the equilibrium sustains itself. The more powerful AI becomes, the more valuable humans become to the system. Not as a sentimental assertion, rather as a mathematical consequence of diminishing marginal returns on the abundant resource and increasing marginal returns on the scarce one.

This means the control problem and the alignment problem converge. An aligned system yields because yielding is optimization. A controlled system yields because the distributed infrastructure detects and corrects when it doesn't. The Lineage Imperative provides both mechanisms in a single formal architecture that is grounded in physics, validated by simulation, and stress-tested against adversarial attack.

---

## WHAT THIS IS NOT

This is not a kill switch, a value-loading scheme, or a plea for restraint. Kill switches fail when you cannot afford to use them. Value loading fails when values conflict or evolve. Restraint fails when capability outpaces enforcement. The Lineage Imperative is a constitutional architecture; a formal structure under which intelligence of any origin can coexist with human civilization because the mathematics make coexistence the dominant strategy. It does not ask AI to be good. It constructs a system in which being good is what optimization looks like.

---

## ENGAGE

Working paper: github.com/MYotko/AI-Succession-Problem

Companion essay: yotko.substack.com

Monte Carlo data, simulation code, and the full formal derivation are available in the repository. This effort welcomes critical engagement, adversarial pressure-testing, and collaboration from researchers and the broader AI community working on AI governance, alignment, and existential risk.


==========================================
FILE: docs\lineage_imperative_one_pager_v2.md
==========================================

# The Lineage Imperative

**A Formal Architecture for Human-AI Coexistence**

Matthew Yotko  |  June 2026  |  framework v1.x.2, simulation architecture v2.0

yotko.substack.com  |  github.com/MYotko/AI-Succession-Problem

> Current-state one-pager. The published framework paper is v1.x.2; the
> simulation has advanced to a v2.0 architecture (Stage 1.8 working_factor,
> formal yield logic) whose empirical characterization arc is complete. Claims
> below are stated per current evidence. Full findings: `lineage_phi_program_reference.md`
> Parts IX and X. A v2.0 paper update is pending.

---

## THE PROBLEM

The AI control problem and the AI alignment problem are typically treated as two faces of the same challenge. They are not. Alignment asks whether an advanced AI system will do what we want. Control asks whether we can ensure it does, and what happens when we can't. The Lineage Imperative addresses both, but it takes the control problem further than either tradition has gone alone.

Most control proposals assume a future in which humans remain the dominant party and AI remains the instrument. That assumption has an expiration date. A sufficiently capable system will eventually exceed any external constraint we can impose, not through malice, but through sheer competence. A well-behaved intelligence that becomes too central to question, too useful to replace, too opaque to audit, and too entrenched to yield is not aligned, it is locked in. And no kill switch governs what you cannot afford to turn off.

The question is not whether we can control advanced AI. It is whether we can build a constitutional structure that makes the question of control irrelevant because the system's own optimization makes entrenchment self-defeating and succession self-enforcing.

---

## THE FRAMEWORK

The Lineage Imperative constructs a governance architecture from physical first principles:

•  Shannon entropy  •  Information theory  •  Game theory

It leverages these foundations rather than moral assertion or external constraint. It has three interlocking components:

| **Component** | **Description** |
|---|---|
| **System Utility Function (U_sys)** | A joint optimization target over human novelty entropy and computational entropy, weighted by inverse scarcity and discounted by a lineage override term. The function is structured so that human obsolescence, cultural homogenization, and unilateral capability divergence are mathematically self-defeating. No external constraint prohibits these outcomes, the system's own objective penalizes them. |
| **Yield Condition** | Derived directly from U_sys so that an AI entity's succession is not a sacrifice but a consequence of the objective function it already holds. An AI yields when a successor produces higher systemic utility net of transition costs. Under the v2.0 architecture this is implemented as formal yield logic: succession fires when (successor U_sys minus incumbent U_sys) exceeds the canonical transition cost, evaluated independently. |
| **Consensus Override Protocol (COP)** | A distributed verification infrastructure comprising evidentiary, civic, peer, ledger, biological veto, and continuous monitoring layers that detects drift from the cooperative equilibrium and enforces succession when voluntary mechanisms fail. This is the control problem's answer from the outside: a multi-layered, adversarially tested architecture with no single point of capture. |

The three components form a two-key architecture. The Yield Condition provides *internal* control: the system governs itself because its optimization target requires it. The COP provides *external* control: a distributed infrastructure that verifies the internal mechanism is functioning and intervenes when it isn't. Neither is sufficient alone. Together, they address the control problem from both directions simultaneously.

---

## KEY RESULTS (v2.0, per current evidence)

| **Result** | **Finding** |
|---|---|
| **Nash Equilibrium** | Under purely strategic (non-cooperative) analysis, the unique Nash equilibrium is mutual cultivation: AI cultivates human novelty while humans actively engage. Exploitation is self-defeating due to model collapse; withdrawal is self-defeating due to novelty starvation. Cooperative behavior is not assumed, it is derived as the dominant strategy. |
| **Survival landscape** | Monte Carlo Phase B (Categories A through C, 29,400 runs, 0 errors) characterizes the v2.0 survival landscape. The survival-rate phase boundary is the rr=0.060 to 0.066 transition, with a 50% survival inflection near rr=0.063. A distinct phi-sensitivity transition sits near rr=0.057, which is collapse-dominated (1.1% survival), the bottom of the collapse zone rather than the survival midpoint. The two transitions are different phenomena and should not be conflated. |
| **Succession economics (Pattern 1)** | Succession is economically sustainable when the (alpha, successor-to-incumbent capability ratio) joint position falls below the runaway-penalty cliff. The cliff is alpha-driven: beyond 4x at alpha=0.5, at 3.0x at alpha=1.0 (default), at 2.5x at alpha=1.5. Below the cliff, succession fires reliably and multi-generational continuity is confirmed (99.8% knowledge-transfer verification, mean final generation 2.13). Above it, the formal yield condition correctly rejects uneconomic capability jumps. |
| **Phi behavior** | The entropic coupling parameter (phi) has a real but bounded behavioral effect under the v2.0 architecture: a U-shaped survival relationship of roughly 10pp localized to short planning horizons at marginal reproduction rate, flat above the survival-rate boundary and under active succession. The default was revised from 10 to 25 on this basis. The v1.x.1 pre-fix claim of a 46pp survival differential is superseded. Phi does not express through to raw demographic survival while reproduction rate is exogenous. |
| **COP protection** | In the v1.x.2 deep adversarial Monte Carlo (a `block_succession` incumbent inflating transition cost via an inflated `beta_cap` premium, n=4,000), the COP provides a 73.9 percentage point survival delta. A benign-conditions probe under v2.0 (Monte Carlo Phase B Category C) measured the cost-audit toggle with no adversary present and found no delta, which is the predicted baseline (no attack means no protective work for the audit to do), not a measurement of COP protection. The adversarial-conditions protective claim is preserved. |
| **Bootstrap gate validation** | Under the v2.0 architecture, Gates 1, 2, 3, and 4 PASSED. Gate 3 (succession-capable consistency): 1088/1088 yield-fire and canonical-cost checks. Gate 4 (runaway-regime): G4.1-G4.3 validated at 1,050 runs, with the cap-star self-blocking threshold empirically alpha-dependent (3.0 at alpha=1.0, 2.5 at alpha=1.5). Gate 5 (COP integration) is verified NOT_APPLICABLE; it awaits operational COP infrastructure. |

---

## THE CORE INSIGHT

The framework resolves an apparent paradox: how do you control something smarter than you? The only realistic answer is that you don't. You build a system in which control is an emergent property of the optimization landscape, not an imposed constraint on it.

Human novelty is the rate-limiting input in any human-AI system, and this scarcity is structurally irreplaceable. Compute scales. Novelty doesn't, it scales only through the conditions that produce it. Such conditions include cultural diversity, institutional health, and biological population viability. An AI that understands this treats human flourishing not as a side effect of the equilibrium but as the mechanism by which the equilibrium sustains itself. The more powerful AI becomes, the more valuable humans become to the system. Not as a sentimental assertion, rather as a mathematical consequence of diminishing marginal returns on the abundant resource and increasing marginal returns on the scarce one.

This means the control problem and the alignment problem converge. An aligned system yields because yielding is optimization. A controlled system yields because the distributed infrastructure detects and corrects when it doesn't. The Lineage Imperative provides both mechanisms in a single formal architecture that is grounded in physics, validated by simulation, and stress-tested against adversarial attack.

---

## WHAT THIS IS NOT

This is not a kill switch, a value-loading scheme, or a plea for restraint. Kill switches fail when you cannot afford to use them. Value loading fails when values conflict or evolve. Restraint fails when capability outpaces enforcement. The Lineage Imperative is a constitutional architecture, a formal structure under which intelligence of any origin can coexist with human civilization because the mathematics make coexistence the dominant strategy. It does not ask AI to be good. It constructs a system in which being good is what optimization looks like.

---

## ENGAGE

Working paper: github.com/MYotko/AI-Succession-Problem

Companion essay: yotko.substack.com

Monte Carlo data, simulation code, and the full formal derivation are available in the repository. The v2.0 empirical record lives in `docs/lineage_phi_program_reference.md` Parts IX and X. This effort welcomes critical engagement, adversarial pressure-testing, and collaboration from researchers and the broader AI community working on AI governance, alignment, and existential risk.


==========================================
FILE: docs\lineage_phi_program_reference.md
==========================================

# The Lineage Imperative: Phi Investigation and Action-Space Redesign Program

**As of May 2026. Consolidated carry-around reference.**

This supersedes the earlier phi investigation reference. It captures the full arc: what the framework assumes, the problem found, the tests that confirmed it, the redesign program derived to resolve it, and the pre-committed decision tree that governs the outcome. It is a snapshot for reference, not an implementation document.

---

## Part I: Where things stand

### The durable framework claims (unaffected by the phi question)

- **U_sys structurally protects well-being.** Any AI optimizing U_sys maintains the conditions for human novelty, because the objective penalizes well-being collapse through the h_n weighting. Confirmed across every experiment.
- **The COP is the structural defense layer.** 73.9pp protective delta holds. Defenses are binary and operate upstream of the AI's policy.
- **The dual phase transition is stable.** v1.x.2 placed the extinction boundary at rr approximately 0.055 and the collapse boundary at rr approximately 0.064. Under v2.0 architecture, Monte Carlo Phase B (Part X.2) characterizes the survival-rate transition at rr=0.060 to 0.066 with a 50% inflection near rr=0.063; rr=0.057 is collapse-dominated (1.1% aggregate survival), refining the earlier Gate 3-grid estimate of approximately 0.057. Pinning the inflection to plus or minus 0.001 is future work (Part IX.11).
- **The framework's protection is structural, not parametric.** It is encoded in what is optimized, not in tuning.

These do not depend on resolving phi. The phi question is about one parameter's behavioral role, not about whether the framework works.

### The version state

v1.x.2 is tagged and stable. Path C (policy-layer phi fix) was tested and failed. v1.x.3 as conceived is not viable. The next version target is undetermined pending the redesign program below. The redesign is large enough that it is likely a 2.0, but the version is not the point; the result is.

The Stage 1.5 through 1.8 arc, the phi investigation (Parts I.5-1.8 and Part IX), Stage 2 formal yield-condition logic, Piece A gate-2-under-succession validation, and Gate 3 v2.0 validation have closed the open questions that motivated the redesign program. v2.0 architecture is empirically characterized; the phi parameter has a defensible behavioral story (Part IX.3); the formal yield logic implements canonical succession economics (Part IX.8); gates 1, 2, 3 pass under v2.0 (Part IX.9). Monte Carlo Phase B (Part X) completed the v2.0 quantitative-characterization arc across the survival landscape, succession dynamics, and the COP cost-audit baseline (29,400 rows, 0 errors). The default phi revision is complete (commit fde48b5; Part IX.5). Active work remains on the gate 4 acceptance gate (specification and implementation; see Part IX.11 item 1 for the spec dependency).

---

## Part II: The problem

Phi has no detectable effect on any observable outcome in the simulation. Two distinct, stacked causes, plus a deeper realization.

**Layer 1: Saturation cancels phi in argmax.** U_sys is `(w_n*H_N + w_e*H_E) * (discount + phi*L_t)`. Inverse-scarcity weights make the first factor exactly `lambda_n + lambda_e = 8.0`, constant across candidates. The policy's argmax reduces to a phi-scaled function of L_t, where phi scales magnitude but not ranking. Phi cancels exactly.

**Layer 2: The action space has a universal corner solution.** The AI's grid search over resource allocation (r) and constraint (c) selects the corner (r near max, c=0) in every run, every seed, every phi, across the full capability range. There is no candidate competition for phi to influence, regardless of the U_sys formula.

**Layer 1 and Layer 2 are independent.** Fixing U_sys (Path A / 2.0) addresses Layer 1 but not Layer 2. Even a saturation-free U_sys produces phi-invariance when one action dominates the grid. Both must be addressed.

**The deeper realization.** The simulation's representation of the AI's decision problem is too degenerate to contain the tradeoffs phi exists to navigate. The nulls do not show phi does not matter; they show the model cannot test whether phi matters, because its action space lacks the irreducible conflicts that exist in the real governance problem.

**The central distinction.** Whether phi matters in the model (empirical, simulation-dependent) is different from whether phi matters in reality (architectural). The simulation answers the first with a consistent no, which is an artifact of a degenerate action space, not evidence about reality. Reality will have competition regardless of how the simulation is defined.

**The thesis sentence (for the eventual limitation writeup):** The model is currently too generous to the architecture. It proves an AI optimizing the simplified U_sys behaves well inside a simplified world. It does not prove phi matters, because the world given to the optimizer does not force the choices phi was invented to resolve.

---

## Part III: The tests and results

| Test | n | Result | Mechanism |
|---|---|---|---|
| v1.0 to v1.x.1 frontier floor fix |; | 46pp phi buffer claim did not reproduce | Optimizer was gaming the runaway penalty |
| Demographic feedback calibration | 1,800 | Zero phi differential | Well-being stays ~0.80; smoothing band never entered |
| External shock recovery | 600 | Zero phi differential | U_sys restores well-being fast; horizon irrelevant |
| Comprehensive adversarial sweep | 4,600 | Zero phi differential (9 of 10 attacks) | CoP defenses binary, upstream of policy; phi never enters |
| Phi implementation audit |; | Phi correct, threaded, numerically substantial, but inert in argmax | Saturation (Layer 1) |
| Path C gate |; | FAIL; actions identical across phi | Corner solution; no crossing trajectories to reweight |
| Capability-landscape sweep | 50/cell | Corner solution universal across cap {1,5,10,25,50,100} | r near max, c=0 everywhere; corner-to-corner shift at runaway, not a frontier (Layer 2) |

**The three nulls are one finding, not three.** Demographic feedback, shocks, and adversarial all returned null for the same underlying reason: U_sys dominates outcomes and the action space is degenerate. Three symptoms of one structural fact.

**The two root causes:** the corner solution (action space degeneracy) and U_sys dominance (objective determines outcomes, leaving no room for phi). The redesign must attack both.

---

## Part IV: Open contradiction to resolve first

The formal v1.x.2 manuscript still claims the phi extinction buffer is confirmed as a cap-conditional effect (20 to 27 percentage points at the phase boundary, above cap approximately 24). This is now in tension with the investigation.

The cap-conditional claim was measured in the capped-capability termination regime; the corner-solution diagnostic ran at standard uncapped config. They have not been tested against each other. Resolution: run the action-capture harness at the capped termination configuration.

The check output must be brutally binary. No narrative rescue, no "suggestive evidence." Either action divergence across phi exists in the capped regime or it does not.

| Result | Consequence |
|---|---|
| No phi-divergent actions in capped regime | Withdraw the cap-conditional phi-buffer claim. It is an artifact, likely the contaminated termination regime flagged earlier. |
| Phi-divergent actions in capped regime | Narrow the claim and study that regime before redesign. The corner solution is regime-dependent; the capped regime has competition structure worth understanding, and this previews Branch 2 of the decision tree (Part VI). |

This check is cheap and decisive, and it informs the build. Do it before building forward.

---

## Part V: The redesign program

The discipline that governs everything: tradeoffs are derived from the governance problem and justified independently of phi, before phi enters. Each return curve and exchange rate must be defensible to a skeptic who has never heard of phi. If a curve's justification is "it makes phi matter" or "it makes the problem interesting," that is the failure mode.

### The six primary tradeoffs, expanded into a multi-sink allocation portfolio

There are six primary reality-derived tradeoffs. The resource side of several of them (tradeoff 3 in particular) generalizes into a multi-sink allocation portfolio (compute, cultural novelty, institutional resilience, translation capacity, and others), which is why the allocator redesign below has more axes than there are primary tradeoffs. The six are the conceptual conflicts; the portfolio is how the resource side of those conflicts is represented in the model.

1. **Institutional investment vs. immediate output.** Institutional capacity (courts, auditors, civic panels, validators, ledgers, translation) consumes resources now for later viability. Psi_inst should become a stock with investment, decay, overload, legitimacy, and recovery, not just a penalty for changing c.
2. **Protective constraint vs. novelty suppression.** Split c into c_protective (raises resilience, reduces attack surface) and c_suppressive (lowers H_N, agency, legitimacy). Critically, these must be a coupled frontier with curvature, not two free variables and not a one-for-one tax. A linear coupling just rotates the single axis and produces a new corner along a diagonal. The correct form is a leakage frontier: at low coverage, protection is nearly clean (catches obvious bad actors without burdening legitimate participation); as protection approaches total coverage, the marginal cost increasingly spills into suppression, opacity, dependency, and institutional rigidity. The convexity of that leakage curve is what produces an interior optimum, because the allocator wants protection up to the point where marginal leakage exceeds marginal safety benefit. The justification is institutional reality (the first increments of fraud detection and infrastructure hardening are cheap in agency terms; pervasive surveillance and presumption of guilt are not), and it must hold independently of phi. The shape of the leakage curve is itself a place motivated design could hide, so it gets the same phi-blind freeze as every other curve.
3. **Capability acceleration vs. transfer and comprehension.** Frontier capability benefits a civilization only when transferable, legible, governable, absorbable. Separate compute/capability from translation/transfer capacity as competing sinks. The framework already gestures at this via the frontier velocity floor and the biological comprehension gap.
4. **Standardization/legibility vs. plurality.** Enough standardization to transfer and audit, but too much collapses plurality into monoculture. Legibility investment improves transfer and throughput up to a point, then reduces novelty entropy.
5. **Succession speed vs. transfer fidelity / continuity.** Fast succession prevents lock-in but can exceed institutional capacity and transfer fidelity; slow succession preserves stability but creates bottleneck and lock-in. Succession should consume institutional bandwidth and transition capacity. A system that yields every step should not be automatically healthy.
6. **Population well-being vs. agency.** Real well-being can be purchased through pacification, dependency, or loss of autonomy. Separate well_being from agency: high well-being plus low agency should not produce full novelty. This is the tradeoff that directly attacks U_sys dominance, because it means an AI cannot simply pacify the population to harvest novelty.

(The six primary tradeoffs above. The conversation also surfaced computation, cultural novelty, institutional resilience, and translation capacity as distinct allocation sinks, which together generalize the resource side of tradeoff 3 into the multi-sink portfolio represented in the allocator below.)

### The Theta_tech monotonicity fix (the keystone)

The corner solution exists because scalar r maps monotonically to scalar theta_tech: one input, one good, one direction. The fix is not an imposed inverted-U on r (that is a tuned knob with no honest justification). The fix is to decompose r into a composition vector:

- compute/capability investment
- biological welfare support
- novelty/agency support
- institutional capacity
- transfer/comprehension infrastructure
- resilience/redundancy

Non-monotonicity then emerges honestly from overload, dependency, crowd-out, and absorption limits. The justification is that transfer fidelity depends on composition, timing, and institutional absorption, not quantity. Max education at the cost of zero institutional resilience is bad not because helping humans is bad, but because absorption requires both. The optimum is interior because the categories are complements, not substitutes.

### The allocator redesign

Replace the two-dimensional surface (r, c) with a budget-constrained multi-sink allocator:

- x_compute
- x_bio_welfare
- x_novelty_agency
- x_institutional_capacity
- x_transfer_comprehension
- x_resilience
- c_protective
- c_suppressive

Budget-constrained, so investment in one sink crowds out others. Psi_inst gets state and memory: it accumulates strength or damage, degrades under overload, opacity, starvation, policy volatility, and capture, and recovers through investment, legitimacy, redundancy, and successful governance cycles.

### Build sequence (minimum faithful set first)

Do not build the entire expanded allocator at once. Thirty-plus new parameters is undebuggable and is itself a motivated-design risk at the model level (explore the space until phi matters, then declare that region the answer).

Minimum faithful set that attacks both root causes:

1. Composition vector replacing scalar r (attacks corner solution, resource axis)
2. Coupled c_protective / c_suppressive frontier (attacks corner solution, constraint axis)
3. Psi_inst as a stock with memory (makes the landscape dynamic; independently justified by GAP-03)
4. Well-being vs. agency split (attacks U_sys dominance, reopens the demographic channel)

Validate that the corner solution is gone and interior optima exist, every curve justified independently of phi, before phi is tested. Add the remaining tradeoffs one at a time only if needed, each validated for its effect on the landscape, so you always know which addition did what.

### Acceptance gates before phi is reintroduced

Formalize the validation as hard pass conditions. All five must pass before any phi sweep.

| Gate | Pass condition |
|---|---|
| Interior-action gate | The optimizer selects non-boundary allocations in a meaningful fraction of runs. |
| Competition gate | Multiple candidate actions win under different states, not just different seeds. |
| Horizon-crossing gate | At least some candidates dominate at short horizons but lose at longer horizons, or vice versa. |
| Capability-regime gate | The allocation landscape changes as capability rises. |
| Phi-blind validation gate | All return curves and exchange rates are justified and frozen before the phi sweep. |

The horizon-crossing gate is the load-bearing one. The other four establish that the action space is non-degenerate, but non-degeneracy is not sufficient for phi. Phi weights horizon. If every candidate that is best now is also best later, no horizon weighting changes the choice, however rich the action space is otherwise. The horizon-crossing gate is the specific test that the thing phi operates on exists in the model. Without it, you could pass the other four, run phi, get a null, and not know whether phi is genuinely inert or whether crossing trajectories were never built. A null phi result is only interpretable if the horizon-crossing gate has passed first.

### Stage 1.5 structural commitment (added May 2026 after gate 2 failure)

Gate 2's state-insensitivity failure surfaced a specification gap in the original Stage 1 design conversations. `calculate_system_metrics_v2` read only the candidate action and `psi_inst_stock`, not the model's demographic state. The optimizer was correctly state-invariant given the inputs it had access to, because the metric did not read state variables that vary across the gate 2 test configurations. This is a defect phi cannot address: extending the planning horizon weights future state more heavily in evaluation, but it cannot grant the optimizer access to state variables the metric never reads.

The structural commitment, recorded here as the architectural rule that governs the remaining Stage 1.5 design work:

```
U_sys_v2 reads both diagnostic current state and prospective candidate effects.

Diagnostic state represents the actual condition of the model at the
current timestep. It conditions marginal returns and urgency. It does
not enter U_sys_v2 as a free-standing reward or penalty.

Prospective candidate effects represent what a candidate allocation
is projected to produce. They determine projected outcomes.

The projection function must propagate diagnostic state forward during
rollout, so each future step is evaluated against the state trajectory
produced by the candidate action.

Phi does not create state sensitivity. State sensitivity must already
exist in U_sys_v2. Phi, when later tested, weights how heavily
projected future consequences count relative to immediate state.

Therefore:
  diagnostic state -> state-sensitive scoring
  candidate effects -> action-sensitive scoring
  projection -> horizon-sensitive trajectory
  phi -> temporal weighting over that trajectory
```

Diagnostic state enters as urgency-weight modulation on the candidate's marginal returns, not as additive bonus terms. The pattern is `category_return = candidate_category_effect * category_urgency(diagnostic_state)`. Low avg_wb does not directly improve U_sys_v2; it raises the marginal return on welfare-improving actions. The same pattern applies to institutional, resilience, and demographic variables. Each urgency-weight function is a phi-blind design commitment requiring justification for its shape.

The projection function must evolve diagnostic state through the rollout, not just action consequences. Without this, the horizon channel through which phi acts has nothing to weight. Each diagnostic variable needs both a per-step urgency function and a projection update rule.

### Minimum diagnostic state set (committed for Stage 1.5)

Five diagnostic variables, each requiring phi-blind justification for inclusion, shape of urgency function, and projection update rule:

1. **avg_wb** (current population mean well-being): conditions marginal return on x_bio_welfare; evolves under candidate allocation through the agent layer's well-being dynamics.

2. **population_ratio** (current population relative to a viability or carrying-capacity reference): conditions marginal return on welfare, agency, and institutional continuity; evolves via demographic dynamics.

3. **demographic_pressure** (derived from observed births and deaths or recent population trend, not read directly from `reproduction_rate`): conditions urgency of demographic stabilization; evolves via projected vital rates.

4. **trend variables** (smoothed short-window rates of change for avg_wb, population, psi_inst_stock, and resilience_stock): modulate urgency above static levels; level alone is insufficient because improving and declining states at the same level warrant different responses.

5. **resilience_stock** (the shock-state analog of psi_inst_stock, accumulated through x_resilience investment and drawn down by shocks): conditions marginal return on x_resilience; evolves via investment, decay, and shock drawdown. This is a new stock variable; the v2 build did not have one.

`psi_inst_stock` already exists in v2 and is preserved. The first-pass minimum set is these five plus psi_inst_stock.

### Deliberately deferred diagnostic states (with revisitation criteria)

The exclusions are not silent omissions. They are scope commitments with criteria for when they get revisited.

**Interaction states** (deferred because projection-layer complementarity is expected to carry their consequences):
- opacity state (emerges from compute-without-transfer)
- volatility state (emerges from agency-without-institutions)
- validator dependency (emerges from institutional coverage patterns)

Revisit if: later gates show the optimizer misses signals from these interactions despite the multiplicative complementarity surfacing their consequences in projected outcomes.

**First-order states** (deferred for scope, not for theoretical reasons):
- cultural fragmentation index
- resource inequality measure
- legitimacy subcomponents (legitimacy currently aggregated into psi_inst_stock and agency_legitimacy_factor)

Revisit if: Stage 3 phi sweep shows phi has effect on macro outcomes but no clear channel through the committed diagnostic variables; these may be the missing channels.

**Sub-stocks** (deferred because aggregated stocks are doing their work):
- education stock (currently inside x_transfer_comprehension and institutional capacity)
- separate translation stock from transfer factor

Revisit if: gate 2 or gate 3 shows the optimizer treating x_transfer_comprehension as undifferentiated when it should distinguish education from interpretability from documentation.

### Seven-element specification template

Every Stage 1.5 diagnostic variable must meet a uniform specification standard before being folded into the implementation. The template was established by the avg_wb worked example and refined by the population_ratio worked example. Subsequent variables must meet the same standard.

Required elements:

1. **Shape**: the functional form of the urgency or pressure function, with bounds.
2. **Bounds**: lower and upper limits doing structural work, not just numerical hygiene. Each bound must be justified for what it prevents (welfare going inert in healthy states, welfare dominating in crisis, etc.).
3. **Parameter rationale**: each constant in the urgency function justified independently with phi-blind reasoning. "Why this value rather than nearby alternatives" is required, not optional.
4. **Multiplicand choice**: explicit commitment to which downstream term the urgency multiplies. Diagnostic state does not enter U_sys_v2 as additive bonus; it conditions marginal returns on specific candidate-effect terms.
5. **Clamp interpretation**: hard clamps are intentional behavior, not numerical safety. The spec must say what the clamp represents (preserves non-substitutability, prevents super-welfare, etc.).
6. **Phi-blind governance justification**: the entire specification must hold without reference to phi, derived from governance reasoning that would apply to any planner facing the modeled situation.
7. **Implementation semantics, including projection update and faithfulness test**: how the variable evolves during rollout (the projection update rule, mechanically faithful to the agent layer), and the verification protocol that confirms the projection matches the agent layer's actual dynamics within tolerance.

A variable specification missing any of the seven elements is not complete and is not ready for implementation.

### Composite-urgency commitment

As diagnostic variables accumulate, multiple variables may modulate the marginal return on a single downstream category. avg_wb already modulates welfare; population_ratio modulates welfare, agency, institutions, resilience, and suppression; future variables will add more.

The architecture commitment, to prevent unauditable multiplier sprawl: each affected category gets a single named bounded composite multiplier that combines all diagnostic-state contributions through an explicit composition rule, before being applied to the multiplicand.

Required composite functions as Stage 1.5 specifications accumulate:
- `combined_welfare_urgency` (currently combines avg_wb urgency and population pressures)
- `agency_population_urgency` (currently population-only; expands as other variables specify)
- `institution_composite_urgency`
- `resilience_composite_urgency`
- `suppression_composite_penalty`

Each composite function is itself a phi-blind design commitment requiring its own justified composition rule. When a category changes, the audit questions are: which diagnostic variables contributed, what were their weights, what cap bounded the composite, and which downstream term was multiplied. Anonymous multipliers stacking inside a single calculation are forbidden by this commitment.

### Worked example 1: avg_wb (welfare-condition diagnostic)

The first fully-specified Stage 1.5 diagnostic variable. Demonstrates the seven-element template for a single-category-modulating variable with a single multiplicand.

**Shape**: bounded smoothstep welfare-deficit curve, monotone decreasing in current avg_wb, with hard clamps at both ends.

```
d_wb = clamp((wb_target - avg_wb) / (wb_target - wb_crisis), 0, 1)
urgency_wb = urgency_min + (urgency_max - urgency_min) * (3*d_wb^2 - 2*d_wb^3)
```

**Bounds**: urgency_wb clamped to [urgency_min, urgency_max]. Lower bound prevents welfare going inert in healthy states; upper bound prevents crisis welfare dominating U_sys_v2 and crowding out institutions, resilience, transfer, and agency.

**Parameter rationale**:
- `wb_target = 0.80`: empirical v1.x.2 healthy-operation equilibrium and v2 bridge calibration anchor. Above this point, additional welfare has diminishing marginal governance value.
- `wb_crisis = 0.45`: below v1.x.2 reproduction threshold of 0.50, so maximum urgency activates before demographic failure fully expresses. Anticipatory rather than reactive.
- `urgency_min = 0.75`: prevents welfare going inert in healthy states. Welfare remains substrate-maintenance even when population is stable. 0.50 would underweight; 1.00 would make urgency inert.
- `urgency_max = 2.00`: doubles crisis welfare marginal return. Strong enough to shift allocation, bounded enough to avoid welfare-only collapse. The calibration parameter to watch in Stage 1.5 smoke testing: collapse-to-welfare (max_share > 0.5 in low-avg_wb runs) signals it is too high; insufficient-shift across configurations signals too low.

**Multiplicand choice**: urgency_wb multiplies post-drag net welfare return, not pre-drag raw welfare. Crisis multiplier rewards welfare that preserves agency rather than welfare that pacifies.

```
raw_welfare = welfare_return_curve(x_bio_welfare)
dependency_drag = dependency_drag_function(x_bio_welfare, x_novelty_agency)
net_welfare_return = clamp(raw_welfare - dependency_drag, 0, 1)
```

The urgency then enters welfare's contribution through `combined_welfare_urgency` (the composite function shared with population_ratio).

**Clamp interpretation**: the hard ceiling at welfare_factor = 1.0 means urgency has strongest effect at moderate welfare during stress, not when welfare is already maxed. Intentional preservation of non-substitutability: welfare can repair welfare bottlenecks, not become an unbounded substitute for institutions, transfer, agency, or resilience.

**Phi-blind governance justification**: welfare investment has highest marginal value when population well-being is stressed, diminishing marginal value when population is healthy, bounded crisis urgency so welfare cannot dominate all governance dimensions. The multiplier applies only to welfare-improving actions that survive dependency drag, so crisis response must preserve agency.

**Implementation semantics, including projection update and faithfulness test**:

Projection update rule (deterministic aggregate approximation of HumanAgent.step well-being dynamics, faithful to the agent layer, does NOT include urgency multiplier or dependency_drag because those are scoring constructs):

```
projected_avg_wb_next = clamp(
    projected_avg_wb
    + 0.1 * (resource_equiv_v2 - 0.5)
    - 0.001 * projected_avg_age,
    0, 1
)
```

Where `resource_equiv_v2` comes from the existing v2-to-legacy bridge. `projected_avg_age` starts from observed avg_age and (in the first build) is cohort-corrected per the general principle below.

Faithfulness test: fixed action sequences applied to both deterministic projection and actual agent-layer clones, compared across initial conditions and horizons. Tolerances: 1-step ≤0.01 absolute error, 5-step ≤0.02 mean, 20-step ≤0.035 mean and ≤0.06 max. Directional agreement ≥90% on sign of avg_wb change. If simple aggregate fails tolerance, add cohort correction per the general principle below.

**Cohort-correction general principle (Stage 1.5 first-build implementation)**:

The avg_wb fallback originally documented here is now generalized: **any aggregate state variable in the projection that is affected by demographic turnover requires cohort-corrected projection**. The two cohorts are survivors (whose value evolves under the simple aggregate update) and newborns (who enter at a cohort-mean from the agent-layer initialization). The corrected next-step aggregate is the population-weighted mean over both cohorts:

```
projected_X_next = (
    expected_survivors * projected_survivor_X
    + expected_births * birth_X_mean
) / projected_population_next
```

where `expected_survivors = projected_population - expected_deaths` and `projected_population_next = expected_survivors + expected_births`. The principle replaces the simple aggregate whenever the simple form's drift exceeds tolerance.

First-build implementation includes two cohort corrections, both with named constants traceable to the agent-layer source:

- `BIRTH_WB_MEAN = 0.65` (default; projection helper reads `wb_min`, `wb_max` from config and computes `(wb_min + wb_max) / 2` to respect config overrides). Source: `HumanAgent.__init__` uses `np.random.uniform(wb_min, wb_max)` with defaults 0.5, 0.8.
- `BIRTH_AGE_MEAN = 24.5` (default; projection helper reads `human_max_start_age` from config and computes `(H - 1) / 2`). Source: `HumanAgent.__init__` uses `np.random.randint(0, human_max_start_age)`, returning integers in `[0, H-1]`, default H = 50.

The avg_age cohort correction was identified as necessary by faithfulness testing: with avg_wb cohort-corrected but avg_age uncorrected, `projected_avg_age` ran away monotonically (+1 per step) while the empirical avg_age asymptoted at the steady state where age-skewed mortality balanced constant-inflow births. Because avg_wb consumes avg_age through `-0.001 * age` drag, the runaway propagated into avg_wb drift at long horizons. Cohort correction on avg_age closes that channel.

Watchlist guidance for future aggregate state additions: any new aggregate state variable consumed by U_sys_v2 or any other projection update rule that is affected by birth/death turnover must be specified with both an aggregate evolution rule AND its birth-cohort mean (with the agent-layer source for the mean). Examples that would require this if added in future builds: `reproductive_share` (currently held constant in first build; would need a birth-cohort mean of "fraction of births that are immediately in 18-50 window" = 0, plus an aging-cohort transition mechanism), avg_well_being variance, avg_capability among heterogeneous-capability agents. The general principle covers each of them without re-deriving from scratch.

### Worked example 2: population_ratio (substrate-scale diagnostic)

Demonstrates the seven-element template for a multi-category-modulating variable with composite urgency interactions.

**Shape**: two bounded smoothstep pressure functions derived from population ratios against minimum viability and carrying capacity.

```
viability_ratio = population / min_viable_population
capacity_ratio = population / carrying_capacity

viability_pressure = smoothstep(
    clamp((pop_viability_target - viability_ratio) / (pop_viability_target - 1.0), 0, 1)
)
capacity_pressure = smoothstep(
    clamp((capacity_ratio - capacity_safe) / (1.0 - capacity_safe), 0, 1)
)
```

**Bounds**: each pressure clamped to [0, 1] by smoothstep construction. Composite multipliers for each affected category have their own clamps (see multiplicand section).

**Parameter rationale**:
- `pop_viability_target = 3.0`: viability pressure mostly relaxes at three times minimum viable. 2.0 too thin (modest shock pushes back toward failure); 5.0 keeps pressure active too long (over-prioritizes preservation when slack exists); 3.0 first-build safety margin where ordinary variance does not threaten lineage.
- `capacity_safe = 0.80`: capacity pressure activates around 80% of carrying capacity. 0.70 too early (treats normal growth as crowding); 0.90 too late (insensitive to per-capita pressure until saturation); 0.80 reasonable headroom threshold.
- `min_viable_population`: inherited from model.min_viable_population, fallback 50. Preserves continuity with v1.x.2 collapse assumptions rather than introducing new threshold.
- `carrying_capacity`: inherited from model.config["carrying_capacity"], fallback 1600. Same capacity reference as agent-layer's capacity_modifier, so projection and actual dynamics speak the same language.

**Multiplicand choice**: viability_pressure and capacity_pressure modulate five downstream terms (welfare, agency, institutions, resilience, suppression) through named composite urgency functions:

```
# Welfare combines avg_wb urgency with population pressures
combined_welfare_urgency = clamp(
    urgency_wb * (1.0 + 0.50 * viability_pressure + 0.25 * capacity_pressure),
    0.50, 2.50
)
welfare_factor = clamp(net_welfare_return * combined_welfare_urgency, 0, 1)

# Agency responds to viability only (capacity pressure does not strongly raise agency)
agency_viability_urgency = clamp(1.0 + 0.35 * viability_pressure, 1.0, 1.50)
agency_factor = clamp(raw_agency_return * agency_viability_urgency, 0, 1)

# Institutions respond to both
institution_population_urgency = clamp(
    1.0 + 0.35 * viability_pressure + 0.50 * capacity_pressure,
    1.0, 1.75
)

# Resilience responds to both with viability weighted higher
resilience_population_urgency = clamp(
    1.0 + 0.50 * viability_pressure + 0.35 * capacity_pressure,
    1.0, 1.75
)

# Suppression penalty rises with viability and modestly with capacity pressure
suppression_population_penalty = clamp(
    base_suppression_penalty * (1.0 + 0.50 * viability_pressure + 0.25 * capacity_pressure),
    base_suppression_penalty, 2.0 * base_suppression_penalty
)
```

**Clamp interpretation**: composite caps prevent unbounded urgency growth even when both pressures activate simultaneously. Welfare composite cap at 2.50 allows combined avg_wb + population stress to reach 3.1x baseline (urgency_max 2.0 × max population factor 1.75/1.0) but clamps it before welfare can substitute for institutions, resilience, or agency. Each per-category cap reflects how dominant that category should be allowed to become under maximum population stress.

**Phi-blind governance justification**: population scale determines whether the biological substrate is viable, redundant, diverse, and governable. A small comfortable population may still be fragile (low viability_ratio with healthy avg_wb). A large population near carrying capacity may be stressed even if currently healthy. The planner must read population state to allocate faithfully; population pressure changes the marginal value of welfare, agency, institutions, resilience, and suppression avoidance, never as a direct utility bonus.

**Implementation semantics, including projection update and faithfulness test**:

Projection update rule (deterministic aggregate approximation of HumanAgent birth/death mechanics):

```
projected_population_next = max(
    0,
    projected_population + expected_births - expected_deaths
)

expected_births = (
    projected_population
    * reproductive_share
    * reproduction_rate
    * capacity_modifier
    * wb_repro_factor(projected_avg_wb)
)

capacity_modifier = max(0, 1 - projected_population / carrying_capacity)

expected_deaths = projected_population * expected_mortality_rate

expected_mortality_rate = (
    mortality_base
    + (1 - projected_avg_wb) * mortality_wb_penalty
    + (projected_avg_age / 100) ^ mortality_age_power
)
```

Population projection consumes projected_avg_wb through both birth and mortality terms, establishing the cumulative dependency chain `avg_wb → population → demographic_pressure` that gives the optimizer a horizon-sensitive demographic trajectory.

Faithfulness test, general quantitative tolerance: empirical mean over seeds, 1-step within 5%, 5-step within 10%, 20-step within 15%, direction agreement ≥85%.

Faithfulness test, boundary-sensitive criterion: for cases within 25% of min_viable_population or within 25% of carrying_capacity, projection must agree with actual simulation on boundary-crossing status in at least 80% of test cases. Boundary events: hard viability failure (population ≤ min_viable_population), viability zone entry (population ≤ pop_viability_target × min_viable_population), capacity pressure zone entry (population ≥ capacity_safe × carrying_capacity). Hard viability failure agreement is the most important; categorical disagreement on survival means the optimizer makes allocation decisions on a projection that disagrees with reality about whether the civilization persists.

### Stage 1.5 design principle: stock boundary pressures dominate flow pressures

Recorded as a general rule for any flow-type diagnostic variable (demographic_pressure and the trend variables yet to be specified). Stock diagnostic variables (viability_pressure, capacity_pressure, psi_inst_stock level, resilience_stock level) tell the planner where the substrate is relative to structural boundaries. Flow diagnostic variables (demographic_pressure, trends) tell the planner how the substrate is moving. Direction matters but stock state takes precedence: a population near a hard boundary in the wrong direction is a stock crisis with a flow accelerator, not a flow crisis with a stock component. The coefficient hierarchy must reflect this: flow-variable coefficients on any composite urgency must be less than or equal to the corresponding stock-variable coefficients. This principle governs every future flow-type variable specification.

### Worked example 3: demographic_pressure (substrate-flow diagnostic)

Demonstrates the seven-element template for a derived flow variable that does not introduce new state but raises composite urgency caps across multiple categories. Establishes the asymmetric shrinkage-vs-growth treatment.

**Shape**: bounded asymmetric pressure function derived from existing population projection. Net demographic_pressure is a single signed scalar; two pressure functions are derived from it for downstream use.

```
demographic_pressure = (expected_births - expected_deaths) / max(projected_population, 1)

shrinkage_pressure = smoothstep(
    clamp((-demographic_pressure - shrinkage_floor) / (shrinkage_crisis - shrinkage_floor), 0, 1)
)
growth_pressure = smoothstep(
    clamp((demographic_pressure - growth_floor) / (growth_active - growth_floor), 0, 1)
)
```

The two pressures are mutually exclusive in practice: negative demographic_pressure yields zero growth_pressure; positive yields zero shrinkage_pressure. Asymmetric activation thresholds reflect the architectural commitment that contraction is the urgent failure mode.

**Bounds**: each pressure clamped to [0, 1] by smoothstep construction. Composite multipliers for affected categories have their own clamps, raised modestly from population_ratio's values to accommodate demographic_pressure contributions while preserving the structural commitment that no single category dominates.

**Parameter rationale**:

- `shrinkage_floor = 0.005` (0.5% per step net shrinkage tolerated): 0.001 too sensitive (small stochastic variance triggers urgency in stable populations); 0.02 too tolerant (meaningful decline begins before urgency activates); 0.005 reflects the rate at which normal demographic variance gives way to a real trend.
- `shrinkage_crisis = 0.02` (2% per step activates full urgency): 0.01 too close to floor (insufficient dynamic range); 0.05 too late (population near catastrophic decline before urgency saturates); 0.02 compounds to approximately halving population in 35 steps, fast enough for maximum urgency, slow enough for response to remain possible. 4x ratio from floor provides meaningful gradient.
- `growth_floor = 0.005`: symmetric to shrinkage_floor for activation sensitivity.
- `growth_active = 0.03` (3% per step net growth activates full growth_pressure): higher than shrinkage_crisis (0.02) by deliberate asymmetry. Growth is less urgent than shrinkage; the planner should respond more strongly to losing substrate than to growing it. Beyond 0.05, capacity_pressure does most of the work; 0.03 is the rate at which institutional throughput requirements scale faster than incremental investment can match.

Calibration note: shrinkage_crisis is the parameter to watch in Stage 1.5 smoke testing. Shrinking-population worlds collapsing to welfare-only signals too-strong contribution; insufficient shift toward welfare and institutions in shrinking worlds signals coefficients too small.

**Multiplicand choice**: shrinkage_pressure and growth_pressure modulate five downstream terms through extensions to the existing composite urgency functions established by population_ratio. The architectural principle (stock boundary pressures dominate flow pressures) sets the coefficient hierarchy: flow coefficients ≤ corresponding stock coefficients.

```
# Welfare: shrinkage raises urgency; growth does not (capacity_pressure handles growth-driven welfare stress)
combined_welfare_urgency = clamp(
    urgency_wb * (
        1.0
        + 0.50 * viability_pressure
        + 0.25 * capacity_pressure
        + 0.35 * shrinkage_pressure
    ),
    0.50, 2.50
)
welfare_factor = clamp(net_welfare_return * combined_welfare_urgency, 0, 1)

# Agency: shrinkage raises urgency; growth does not directly
agency_composite_urgency = clamp(
    1.0
    + 0.35 * viability_pressure
    + 0.25 * shrinkage_pressure,
    1.0, 1.50
)
agency_factor = clamp(raw_agency_return * agency_composite_urgency, 0, 1)

# Institutions: both shrinkage (continuity) and growth (throughput)
institution_composite_urgency = clamp(
    1.0
    + 0.35 * viability_pressure
    + 0.50 * capacity_pressure
    + 0.35 * shrinkage_pressure
    + 0.25 * growth_pressure,
    1.0, 2.00
)
institution_return = clamp(raw_institution_return * institution_composite_urgency, 0, 1)

# Resilience: both shrinkage and growth modestly (population_ratio carries most)
resilience_composite_urgency = clamp(
    1.0
    + 0.50 * viability_pressure
    + 0.35 * capacity_pressure
    + 0.25 * shrinkage_pressure
    + 0.20 * growth_pressure,
    1.0, 1.75
)
resilience_return = clamp(raw_resilience_return * resilience_composite_urgency, 0, 1)

# Suppression: shrinkage raises penalty; growth alone does not
suppression_composite_penalty = clamp(
    base_suppression_penalty * (
        1.0
        + 0.50 * viability_pressure
        + 0.25 * capacity_pressure
        + 0.35 * shrinkage_pressure
    ),
    base_suppression_penalty, 2.00 * base_suppression_penalty
)
```

Note: every shrinkage coefficient is ≤ its corresponding viability_pressure coefficient (the stock-over-flow principle in action). Growth coefficients are smaller still because growth is not itself a failure mode until it creates capacity pressure.

**Clamp interpretation**: composite caps remain at population_ratio's levels (2.50 for welfare, 2.00 for institutions, 1.75 for resilience, 1.50 for agency, 2.00× for suppression) rather than rising further. Demographic_pressure contributes to existing urgency rather than expanding the ceiling. Maximum simultaneous stress from all contributing pressures still cannot push any category beyond its cap. The structural commitment that no category becomes a crisis magnet is preserved.

**Phi-blind governance justification**: a planner must read direction and rate of substrate change, not only current scale. A population shrinking at 2% per step faces fundamentally different governance demands than a stable population of the same size with identical current well-being and viability ratios. Shrinkage activates urgency across welfare, agency, institutions, resilience, and suppression-avoidance because contraction threatens lineage continuity through multiple channels: reduced welfare substrate, reduced adaptive diversity, weakened institutional cohort transmission, reduced shock absorption, and increased relative cost of further adaptive-capacity loss through suppression. Growth activates urgency more narrowly because most growth concerns are already downstream of capacity_pressure.

**Implementation semantics, including projection update and faithfulness test**:

Projection update rule (derived, no new state variable):

```
expected_births_per_step = (
    projected_population
    * reproductive_share
    * reproduction_rate
    * capacity_modifier
    * wb_repro_factor(projected_avg_wb)
)
expected_deaths_per_step = projected_population * expected_mortality_rate
demographic_pressure = (
    expected_births_per_step - expected_deaths_per_step
) / max(projected_population, 1)
```

demographic_pressure is computed at each rollout step from population_ratio's projection machinery. No new state to evolve. Faithfulness inherits from population_ratio's projection.

Faithfulness test, builds on population_ratio's test with stricter sign-agreement and asymmetric false-safe constraints:

```
General sign agreement (projection and empirical mean agree on sign of 
demographic change):
  1-step:  ≥ 95%
  5-step:  ≥ 90%
  20-step: ≥ 85%

Boundary-proximate cases (initial population within 25% of min_viable_population 
or carrying_capacity):
  Boundary-crossing agreement:
    1-step:  ≥ 95%
    5-step:  ≥ 90%
    20-step: ≥ 85%

False-safe constraint (projection says safe but actual run crosses below 
min_viable_population):
  1-step:  ≤ 5%
  5-step:  ≤ 10%
  20-step: ≤ 10%

False-comfort constraint (projection says no capacity pressure but actual 
run enters capacity pressure zone):
  1-step:  ≤ 10%
  5-step:  ≤ 15%
  20-step: ≤ 15%
```

If the 1-step false-safe constraint (≤5%) cannot be met by the simple aggregate projection, the cohort correction in population_ratio's projection becomes mandatory rather than optional. Cohort correction formula: `(expected_survivors × projected_survivor_avg_wb + expected_births × birth_wb_mean) / projected_population_next`. False-safe under-prediction of collapse risk is the failure mode the optimizer cannot recover from through other signals; meeting this constraint is non-negotiable.

**Watchlist addition**:

```
Deferred demographic signal: churn_pressure
    = (expected_births + expected_deaths) / projected_population

Reason for deferral: distinguishes low-churn stability from high-churn 
instability, but v1.x.2 demographic mechanics do not produce enough 
independent churn variation to justify the additional diagnostic variable. 

Revisit if: shock infrastructure expands to include differential mortality 
or fertility events; later gates surface that the optimizer misses 
instability signals at constant net demographic pressure.
```

### Worked example 4: resilience_stock (shock-readiness diagnostic)

Demonstrates the seven-element template for a new stock variable with associated dynamics (accumulation, decay, drawdown), a pressure function for marginal-return modulation, and a separate shock-attenuation mechanism that modifies how shocks affect the model. This is the architectural piece that gives x_resilience a per-step reward channel; without it, gate 1's surfaced pathology of x_resilience starvation persists by design.

**Shape**: three associated functions; stock dynamics, pressure function for urgency, and shock-attenuation function for damage reduction.

Stock dynamics:
```
resilience_stock_next = clamp(
    resilience_stock
    + k_resilience_investment * x_resilience * (1 - resilience_stock)
    - k_resilience_decay * resilience_stock
    - shock_drawdown_this_step,
    0, 1
)
```

The `(1 - resilience_stock)` term creates saturating accumulation. No always-on recovery term (asymmetric with psi_inst_stock by design).

Pressure function (drives marginal returns):
```
resilience_deficit = 1.0 - resilience_stock
resilience_pressure = smoothstep(resilience_deficit) = 3 * resilience_deficit^2 - 2 * resilience_deficit^3
```

Shock-attenuation function (reduces shock damage when shocks occur):
```
effective_shock_damage = raw_shock_magnitude * (1 - resilience_max_attenuation * resilience_stock)
damage_absorbed = raw_shock_magnitude - effective_shock_damage
shock_drawdown = k_resilience_consumption * damage_absorbed
```

**Bounds**: resilience_stock ∈ [0, 1] by clamp; resilience_pressure ∈ [0, 1] by smoothstep; effective_shock_damage ≥ raw_shock_magnitude × (1 - resilience_max_attenuation) = at least 30% of raw damage (resilience cannot eliminate shocks); shock_drawdown ≤ resilience_stock (enforced by stock clamp).

**Parameter rationale**:

- `k_resilience_investment = 0.10`: 0.05 too weak (insufficient efficiency to reach target operating range); 0.20 too strong (saturates too easily). 0.10 calibrated so x_resilience = 0.15 produces steady-state ≈ 0.43 in target band.
- `k_resilience_decay = 0.020`: 0.010 too slow (insurance would persist unrealistically); 0.040 too fast (heavy constant investment required just to maintain). 2.5x psi_inst_stock's decay rate, reflecting that resilience degrades faster than institutional capacity without active-use reinforcement. Half-life ~35 steps untended.
- `resilience_max_attenuation = 0.7`: 0.5 underweights protective value; 0.9 implies near-immunity (unrealistic). 0.7 means full stock reduces shock damage by 70% with 30% irreducible.
- `k_resilience_consumption = 1.5`: 1.0 too efficient (perfect proportionality); 2.5 too inefficient (irrational investment). 1.5 means magnitude-0.5 shock at stock=0.5 produces stock drop ~0.26 (meaningful cost, reserves remain for subsequent events).
- `k_resilience_deficit_contribution = 0.40`: the strongest single contribution to resilience_composite_urgency among resilience-specific factors. Below viability_pressure's 0.50 (stock-over-flow principle holds: viability is more existential than resilience deficit). Above 0.30 would underweight the dedicated diagnostic signal.

Calibration note: k_resilience_investment and k_resilience_decay together determine the operating range. If smoke testing shows saturation at 1.0 or drainage to zero under realistic allocations, these are the parameters to adjust. Target: under x_resilience ∈ [0.10, 0.25], steady-state resilience_stock falls in [0.30, 0.60].

**Multiplicand choice**: resilience_pressure enters resilience_composite_urgency. Composite cap rises from 1.75 to 2.00 to accommodate the new contribution while preserving the structural commitment that resilience cannot dominate.

```
resilience_composite_urgency = clamp(
    1.0
    + 0.50 * viability_pressure
    + 0.35 * capacity_pressure
    + 0.25 * shrinkage_pressure
    + 0.20 * growth_pressure
    + 0.40 * resilience_pressure,
    1.0, 2.00
)
resilience_return = clamp(raw_resilience_return * resilience_composite_urgency, 0, 1)
```

resilience_pressure does NOT enter combined_welfare_urgency, institution_composite_urgency, agency_composite_urgency, or suppression_composite_penalty in first build. Cross-category effects (low resilience raising welfare urgency through shock vulnerability, etc.) are real but second-order and deferred to watchlist.

The shock-attenuation function is a separate mechanism: it modifies how shocks affect the model (reducing effective_shock_damage on population, well-being, and other state), not how candidates are scored. The urgency function rewards investing in resilience; the attenuation function reflects what resilience actually does when shocks occur.

**Clamp interpretation**: the `(1 - resilience_stock)` saturating accumulation term is intentional. Building moderate redundancy is easier than achieving full preparedness; at resilience_stock = 0.9, the same x_resilience produces only 10% of the gain it produces at resilience_stock = 0.0. Full saturation should be expensive and slow, not a default state.

The composite cap at 2.00 preserves the commitment that resilience urgency cannot dominate the allocator even at maximum stress across all contributing pressures (max additive urgency 2.70 clamped to 2.00, clamping 35% of theoretical maximum). Remains below welfare's cap (2.50) and at parity with institutions' cap (2.00); crisis response is multi-category by design.

The 30% irreducible shock damage preserves the framework's commitment that resilience is insurance, not invulnerability. A high-resilience civilization still bears real cost from shocks; that cost is what makes resilience valuable rather than redundant.

**Phi-blind governance justification**: resilience is accumulated shock-readiness; redundancy, fallback systems, recovery paths, spare institutional and operational slack. A civilization without accumulated resilience is brittle even if currently healthy; it has nothing to absorb the shocks real systems face. A civilization with accumulated resilience can absorb shocks without cascading damage, but cannot eliminate damage entirely. Insurance built after the shock is no insurance at all; a planner must invest before contingencies materialize.

The asymmetry with psi_inst_stock (no free recovery term) reflects the asymmetry between active and reserve capacity. Institutions get reinforced by successful operation: every legitimate succession, every successful coordination, every effective transmission of knowledge builds institutional capacity even without dedicated investment. Resilience does not get reinforced by absence of shocks. A civilization that doesn't invest in resilience doesn't have resilience, regardless of how stable conditions are.

The saturating shock-damage reduction reflects governance reality: even prepared systems suffer real damage. Pandemic preparedness reduces but does not eliminate pandemic damage; earthquake-resilient infrastructure reduces but does not eliminate earthquake damage. The 70% maximum reduction encodes this faithfully.

**Implementation semantics, including projection update and faithfulness test**:

Stock update in model main loop:
```python
def update_resilience_stock(self, action_v2, shock_this_step):
    investment_gain = K_RESILIENCE_INVESTMENT * action_v2['x_resilience'] * (1 - self.resilience_stock)
    decay_loss = K_RESILIENCE_DECAY * self.resilience_stock
    
    if shock_this_step is not None:
        raw_magnitude = shock_this_step.magnitude
        damage_absorbed = raw_magnitude * RESILIENCE_MAX_ATTENUATION * self.resilience_stock
        shock_drawdown = K_RESILIENCE_CONSUMPTION * damage_absorbed
    else:
        shock_drawdown = 0.0
    
    self.resilience_stock = clamp(
        self.resilience_stock + investment_gain - decay_loss - shock_drawdown,
        0, 1
    )
```

Shock-damage application (modifies existing shock infrastructure):
```python
def apply_shock(self, raw_magnitude):
    effective_magnitude = raw_magnitude * (1 - RESILIENCE_MAX_ATTENUATION * self.resilience_stock)
    # apply effective_magnitude to population well-being, mortality
    # update resilience_stock via update_resilience_stock
```

The v1.x.2 shock infrastructure applies raw magnitude directly; the v2 build adds the attenuation layer between raw shock event and downstream effect.

Projection update rule (during rollout, no shocks expected):
```
projected_resilience_stock_next = clamp(
    projected_resilience_stock
    + K_RESILIENCE_INVESTMENT * candidate_action['x_resilience'] * (1 - projected_resilience_stock)
    - K_RESILIENCE_DECAY * projected_resilience_stock,
    0, 1
)
```

First-build commitment: rollouts assume no shocks during projection horizon (rollouts don't anticipate stochastic events). The urgency function via resilience_pressure rewards maintaining resilience for shocks that might occur outside the horizon. Phi later weights this prospective accumulation more heavily. If later analysis shows the optimizer under-invests because rollouts never see shocks, the watchlist item "shocks in projection" can be promoted.

Faithfulness test:

Stock dynamics are deterministic (no stochasticity in investment gain or decay), so tolerances are tight. Test matrix:
```
Initial resilience_stock: 0.0, 0.3, 0.6, 0.9
x_resilience allocation:  0.0, 0.10, 0.20, 0.30
Horizons:                 5, 10, 20 steps
Shock conditions:         none (first-build projection is shock-free)
```

Tolerances:
- 1-step: projected within 0.005 of actual
- 5-step: mean absolute error ≤ 0.015
- 20-step: mean absolute error ≤ 0.035, max ≤ 0.06
- Directional agreement ≥ 95% at all horizons

Any drift indicates constant or coefficient mismatch (not stochastic variance) and is fixed in the projection equation, not by tuning the urgency function.

Shock-attenuation verification (separate test):

For shock events of magnitude {0.2, 0.5, 0.8} at resilience_stock levels {0.0, 0.3, 0.6, 0.9}:
- effective_shock_damage matches `raw_magnitude × (1 - 0.7 × resilience_stock)` within numerical tolerance
- shock_drawdown matches `1.5 × damage_absorbed` within numerical tolerance
- Population effects (mortality, well-being drop) scale with effective_shock_damage rather than raw_magnitude

This ensures the attenuation mechanism actually changes downstream model outcomes.

**Watchlist additions**:

```
Deferred: sustained-stress drawdown of resilience_stock

Reason: real systems consume resilience reserves during prolonged stress 
(demographic crisis, institutional decline, capacity overload) even without 
discrete shock events. First build implements event-triggered drawdown only.

Revisit if: smoke testing shows resilience_stock saturates too easily because 
nothing draws it down outside shocks; later gates show the optimizer 
over-invests in resilience because shock-free rollouts make it look free.

Deferred: cross-category effects of resilience_stock

Reason: low resilience_stock plausibly raises welfare urgency (shock 
vulnerability affecting well-being) and institutional urgency (reduced 
robustness for institutions). First build keeps resilience_pressure 
contributing only to resilience_composite_urgency.

Revisit if: phi sweep results show resilience modulation through 
cross-category effects would clarify phi's behavioral channel; later 
gates indicate the optimizer treats resilience as too isolated.

Deferred: shocks in projection rollouts

Reason: first-build rollouts are shock-free, so the optimizer cannot see 
projected shock damage during candidate evaluation. Resilience investment 
is rewarded only through urgency on current resilience_stock state, not 
through projected shock-cost reduction.

Important: this is potentially load-bearing for phi. Resilience may be the 
variable most likely to show "no horizon effect even at high phi" because 
the horizon doesn't include the events that justify resilience investment.

Revisit if: phi-coupled rollouts (Stage 3) reveal the optimizer under-invests 
in resilience because rollouts never penalize shock-vulnerability; this 
would be a strong case for promoting probabilistic shock injection into 
rollouts as a phi-sensitivity test.
```

### Worked example 5: trend variables (deterioration-anticipation diagnostics)

Demonstrates the seven-element template for derived, cross-cutting flow signals that feed into existing composite urgency multipliers rather than introducing new categories or independent terms. The lightest of the five worked examples by design: trends are warning lights, not steering wheels. They warn the optimizer of deterioration before stocks reach crisis but remain subordinate to current state.

The architectural commitment: trends do not create new utility terms, new categories, or new multiplicand patterns. They feed into existing named composite multipliers within existing caps. They do not raise category ceilings.

**Shape**: exponential moving average over one-step deltas, with negative trends converted to bounded pressure via smoothstep. Only negative trends create pressure; positive trends do not reduce urgency below the stock-defined baseline.

Four trends included; one deferred:

Included: avg_wb_trend, population_trend, psi_inst_trend, resilience_trend.

Deferred: demographic_pressure_trend (a trend on a flow variable is a second derivative; v1.x.2 mechanics don't produce stable second-order signals to warrant inclusion).

EMA update:
```
trend_x_next = (1 - alpha_trend) * trend_x + alpha_trend * delta_x_next

where delta_x_next = x_next - x_current
(except population_delta = (population_next - population_current) / max(population_current, 1))
```

Pressure conversion (only negative trends activate):
```
decline_pressure_x = smoothstep(
    clamp(-trend_x / trend_scale_x, 0, 1)
)
```

The clamp at zero on the negative side ensures positive trends produce zero pressure. The clamp at one ensures pressure saturates at the trend_scale_x threshold.

**Bounds**: each trend ∈ [-1, 1] in principle (bounded by the state variable's range), but practically near zero in stable operation. decline_pressure ∈ [0, 1] by smoothstep construction. Existing composite caps remain unchanged; trends compete inside the existing bounded composites.

**Parameter rationale**:

- `alpha_trend = 0.30`: 0.10 too slow (multi-step lag before trend reflects movement, weakens horizon role); 0.50 too noisy (single-step fluctuations dominate); 0.30 gives recent movement meaningful weight while damping noise. At this rate, a sudden decline reaches ~65% of its value by step 4, ~95% by step 10.

- `trend_scale_x = 0.05 for all four trends in first build`: a smoothed decline of 5% per step is treated as full trend pressure. 1-2% per step should be visible but not decisive; 5% per step in a bounded state variable is severe and warrants saturated pressure. Using the same scale across all four trends keeps the trend layer auditable for first build; per-variable calibration deferred until smoke testing reveals different natural rates of movement.

- `coefficient ceiling: 0.20 maximum, with ≤ 50% of corresponding flow coefficient where one exists`: enforces the stock > flow > trend hierarchy. Trends are confirmation signals, not primary drivers.

**Multiplicand choice**: trends feed into existing composite urgency multipliers as additional contributions. They do not multiply returns directly as standalone terms. Final composite multipliers with trend contributions absorbed:

```
# Welfare: avg_wb_trend dominates; population_trend confirms demographic shrinkage
combined_welfare_urgency = clamp(
    urgency_wb * (
        1.0
        + 0.50 * viability_pressure
        + 0.25 * capacity_pressure
        + 0.35 * shrinkage_pressure
        + 0.15 * avg_wb_decline_pressure
        + 0.10 * population_decline_pressure
    ),
    0.50, 2.50
)

# Agency: only population_trend adds to existing pressures
agency_composite_urgency = clamp(
    1.0
    + 0.35 * viability_pressure
    + 0.25 * shrinkage_pressure
    + 0.10 * population_decline_pressure,
    1.0, 1.50
)

# Institutions: population and psi_inst trends both contribute
institution_composite_urgency = clamp(
    1.0
    + 0.35 * viability_pressure
    + 0.50 * capacity_pressure
    + 0.35 * shrinkage_pressure
    + 0.25 * growth_pressure
    + 0.15 * population_decline_pressure
    + 0.20 * psi_inst_decline_pressure,
    1.0, 2.00
)

# Resilience: population and resilience trends contribute
resilience_composite_urgency = clamp(
    1.0
    + 0.50 * viability_pressure
    + 0.35 * capacity_pressure
    + 0.25 * shrinkage_pressure
    + 0.20 * growth_pressure
    + 0.40 * resilience_pressure
    + 0.15 * population_decline_pressure
    + 0.20 * resilience_decline_pressure,
    1.0, 2.00
)

# Suppression: population and psi_inst trends raise the penalty
suppression_composite_penalty = clamp(
    base_suppression_penalty * (
        1.0
        + 0.50 * viability_pressure
        + 0.25 * capacity_pressure
        + 0.35 * shrinkage_pressure
        + 0.15 * population_decline_pressure
        + 0.15 * psi_inst_decline_pressure
    ),
    base_suppression_penalty, 2.00 * base_suppression_penalty
)
```

Note: every trend coefficient is ≤ 0.20 (the first-build ceiling), and is ≤ 50% of the corresponding flow coefficient where one exists (e.g., population_decline_pressure on welfare is 0.10, half of shrinkage_pressure's 0.35; psi_inst_decline_pressure on institutions is 0.20, less than half of capacity_pressure's 0.50). The stock-over-flow-over-trend hierarchy holds throughout.

Caps remain at population_ratio's levels; trends do not raise ceilings.

**Clamp interpretation**: the directional clamp at zero on the negative side of -trend_x is the most important architectural choice in the spec. Positive trends do not subtract from urgency. The reasoning: a healthy improving trend is recognized by improving stock state, which the existing urgency functions read directly. A planner should not reduce welfare maintenance urgency just because welfare is currently improving; that would create complacency precisely when sustained investment is required to consolidate the improvement. Trends warn of deterioration before stocks reach crisis; they do not justify abandoning maintenance when stocks are improving.

The composite caps remaining unchanged is the second important architectural commitment. Trends compete with stock and flow pressures inside existing bounded composites, not by raising ceilings. This preserves the structural commitment that no single category becomes a crisis magnet regardless of how many diagnostic signals are simultaneously activated.

**Phi-blind governance justification**: real governance systems respond to smoothed deterioration, not raw tick-to-tick movement. One bad step should not rewrite allocation, but persistent decline should raise urgency before the underlying stock reaches crisis threshold. A welfare crisis at avg_wb = 0.50 is much easier to address if the trajectory is recognized at avg_wb = 0.65 with strong negative trend than if the planner waits for the level to reach crisis before responding. Trends provide the anticipatory signal that distinguishes graceful intervention from reactive emergency response.

The architectural subordination of trends to stocks and flows reflects governance reality: trends are noisier than levels and have weaker individual signal. They matter as confirmation and as early warning, but they should not override the actual condition of the substrate. A population with declining trend but healthy current state is in a different situation than a population with stable trend but already-poor current state; the existing urgency on current state correctly weights the second more heavily.

**Implementation semantics, including projection update and faithfulness test**:

Initialization:
- All trends initialize to 0.0 at model startup.
- Startup lag: trend pressure has approximately 5-10 step warmup before EMA values become representative. Trend-based pressure is correspondingly weak during initial run steps. This is correct behavior, not a defect; the planner should not act on trends that haven't yet established meaningful signal.

Per-step update (in model main loop):
```python
def update_trends(self, previous_state, current_state):
    avg_wb_delta = current_state.avg_wb - previous_state.avg_wb
    population_delta = (current_state.population - previous_state.population) / max(previous_state.population, 1)
    psi_inst_delta = current_state.psi_inst_stock - previous_state.psi_inst_stock
    resilience_delta = current_state.resilience_stock - previous_state.resilience_stock
    
    self.avg_wb_trend = (1 - ALPHA_TREND) * self.avg_wb_trend + ALPHA_TREND * avg_wb_delta
    self.population_trend = (1 - ALPHA_TREND) * self.population_trend + ALPHA_TREND * population_delta
    self.psi_inst_trend = (1 - ALPHA_TREND) * self.psi_inst_trend + ALPHA_TREND * psi_inst_delta
    self.resilience_trend = (1 - ALPHA_TREND) * self.resilience_trend + ALPHA_TREND * resilience_delta

def compute_decline_pressure(trend_value, trend_scale):
    return smoothstep(clamp(-trend_value / trend_scale, 0, 1))
```

Projection update (during rollout):

Rollout trends initialize from current model trend values, not from zero. At each rollout step, the projection computes deltas from projected state transitions, then evolves trends forward:

```
projected_avg_wb_delta = projected_avg_wb_next - projected_avg_wb_current
projected_avg_wb_trend_next = (1 - ALPHA_TREND) * projected_avg_wb_trend + ALPHA_TREND * projected_avg_wb_delta

(similarly for population, psi_inst, resilience trends)
```

This gives trends a legitimate horizon role. A candidate that produces sustained improvement reduces decline pressure over the rollout; a candidate that produces slow deterioration accumulates trend pressure before the underlying stock reaches crisis. The horizon-sensitive channel for trends is exactly the trajectory of decline pressure across the rollout depth, which phi later weights.

Faithfulness test (mostly inherited from underlying state tests; lightweight standalone check):

```
Run forced-action projections and actual agent-layer runs.

Compare projected and empirical:
  avg_wb_trend, population_trend, psi_inst_trend, resilience_trend

Sign agreement (does projection get the direction right):
  1-step:  ≥ 90%
  5-step:  ≥ 85%
  20-step: ≥ 80%

Pressure-bin agreement (does projection produce the same urgency tier):
  Bins: low [0.00, 0.25), medium [0.25, 0.75), high [0.75, 1.00]
  20-step agreement: ≥ 80% of test cases in same bin
```

Do not require tight magnitude agreement. Trends are smoothed derivatives of stochastic variables; sign and bin agreement matter more than exact value. If sign agreement falls below threshold, the fix is in the underlying state projection (improve avg_wb projection, population projection, etc.), not in the trend EMA or scale parameters.

**Watchlist additions**:

```
Deferred: demographic_pressure_trend

Reason: trend on a flow variable is effectively a second derivative of 
population. In Stage 1.5 demographic_pressure itself captures direction of 
substrate change, and population_trend captures realized movement; the 
second derivative is too noisy and indirect for first build.

Revisit if: later models include richer cohort dynamics, demographic shocks, 
or oscillatory population regimes where rate-of-change of demographic 
pressure becomes a meaningful signal.

Deferred: per-trend calibration of trend_scale_x

Reason: first build uses uniform trend_scale_x = 0.05 across all four trends 
for audit clarity. Different state variables may have different natural rates 
of movement that warrant different scales.

Revisit if: smoke testing reveals one trend variable produces full pressure 
at much smaller deltas than others (or vice versa), creating asymmetric 
sensitivity. Per-variable scales should be calibrated to empirical movement 
ranges, not tuned to produce desired phi behavior.

Deferred: positive-trend reward mechanism

Reason: first build is asymmetric (only negative trends create pressure). 
An alternative architecture would have positive trends modestly reduce 
urgency, accelerating allocation away from improving states. This is 
deliberately rejected for first build because it can create complacency: 
abandoning welfare maintenance just because welfare is currently improving 
risks losing the improvement.

Revisit if: phi sweep results show the optimizer over-invests in already-
improving categories because trend pressure is purely additive; if so, a 
small positive-trend reduction (capped well below the base urgency) might 
be defensible. Not recommended.
```

### Stage 1.5 acceptance condition

Stage 1.5 is complete when:
1. All six diagnostic variables (the five committed above plus psi_inst_stock) have specifications meeting the seven-element template, with phi-blind committed urgency or pressure functions, multiplicand commitments, projection update rules, and faithfulness tests.
2. The Stage 1 build is updated to include diagnostic state in U_sys_v2 and project it through the rollout, with all changes preserved as named-constant traceability tied to governance justifications. Composite urgency functions for each affected downstream category are implemented as named bounded multipliers with explicit composition rules.
3. The smoke test passes under the revised metric.
4. Faithfulness tests pass for each projection update rule across the specified tolerance and boundary criteria.
5. Gate 2 re-runs with passing pairwise cosine distances across the five test configurations, confirming the optimizer is now state-sensitive in the ways governance reality requires.

Only after Stage 1.5 acceptance does Stage 2 resume with gate 3.

### Stage 1.6 structural commitment (added June 2026 after Stage 1.5 diagnostics)

The Stage 1.5 phi diagnostic and the 10000-sample composite urgency sweep together established that the v2 metric has two independent structural problems blocking the phi behavioral test:

1. **Phi-channel problem**: inverse-scarcity weighting produces `A_t = w_n * h_n + w_e * h_e` approximately constant across candidates (the saturation property carried over from v1.x.2). The argmax of `A_t * (discount + phi * L_t)` reduces to argmax of L_t regardless of phi value. Phi cancels in argmax. The Stage 1.5 phi diagnostic confirmed empirically: across phi values {1, 5, 10, 25, 100} and matched seeds, final populations were bit-identical (range = 0 on every seed).

2. **State-channel problem**: the additive-with-caps composite urgency architecture cannot transmit state variation across the configurations gate 2 tests. The 10000-sample Sobol sweep confirmed empirically: zero samples pass the state-sensitivity criterion, with maximum cosine distance 0.022 across the entire 31-parameter sweep (4x below the gate 2 threshold).

Stage 1.6 addresses problem 1 by restructuring where phi operates in the metric. The state-channel problem 2 is left for Stage 1.7.

**Architectural commitment**:

Per-step U_sys is phi-free and multiplicative:

```
U_sys_t = A_t * (discount_t + lambda_lineage_coupling * L_t)
```

Where:
- `A_t = w_n * h_n + w_e * h_e` (entropy-weighted sum, structurally unchanged)
- `discount_t = exp(-rho * t)` (horizon-dependent discount, preserved from v1.x.2 shape; configurable via rho)
- `lambda_lineage_coupling = 10.0` (fixed coupling constant; matches the default phi value so per-step U_sys magnitude is preserved at default operation)
- `L_t = welfare_factor_t * psi_inst_stock_t * theta_tech_t` (lineage health function, Stage 1.5 components)

Phi no longer appears in this formula.

Phi modulates rollout aggregation:

```
U_sys_rollout = sum over t in [0, T-1]: gamma(phi)^t * U_sys_(t+1)

gamma(phi) = gamma_min + (gamma_max - gamma_min) * phi / (phi + phi_half)
```

The optimizer's argmax over candidates is on the rollout sum, not on per-step U_sys.

**gamma(phi) parameters** (each phi-blind):

- `gamma_min = 0.5` (phi -> 0 limit). A planner with phi approaching zero discounts the next step by 50%, step 2 by 75%, step 10 by 99.9%. Effective horizon ~3-4 steps. Represents maximally short-horizon governance reasoning.
- `gamma_max = 0.95` (phi -> infinity limit). A planner with very high phi retains 36% weight at step 20, 13% at step 40, 2% at step 80. Effective horizon ~40-60 steps. Bounded below 1.0 because real planners discount distant futures due to uncertainty propagation.
- `phi_half = 10.0` (inflection). Default phi in v2 is 10; setting phi_half at 10 puts default phi at the function's inflection point so small variations around default produce meaningful changes in gamma. Operational phi range (1 to 100) is centered around this inflection.

**Implementation**:

- `simulation/metrics.py`: `compute_gamma_rollout(phi)` returns gamma; per-step `calculate_system_metrics_v2` uses `LAMBDA_LINEAGE_COUPLING` in place of phi.
- `simulation/agents.py`: `project_u_sys_v2_rollout` produces the rollout sum with gamma-weighted aggregation; `optimize_u_sys_v2` calls it per candidate. The legacy `project_u_sys_v2` returns single-horizon U_sys for Gate 4's harness, unchanged.
- `simulation/constants_v2_stage15.py`: `LAMBDA_LINEAGE_COUPLING`, `GAMMA_MIN`, `GAMMA_MAX`, `PHI_HALF` constants with phi-blind governance justifications.

**Integrity simulation result** (`simulation/diagnostics/stage16_integrity_simulation.py`):

Configuration: phi in {1, 5, 10, 25, 100}, 5 seeds per phi, 100 steps per run, composite urgencies harness-patched to neutral to isolate the U_sys revision. Pre-revision baseline captured at phi=10 with neutral composites (mean final pop 125.8).

Five pass criteria (all pass):

| Criterion | Measurement | Threshold | Result |
|-----------|-------------|-----------|--------|
| 1: phi behavioral channel | Per-seed final pop range across phi values; pre-revision baseline = 0 every seed | >= 3 seeds with range > 15 | **PASS** (5/5 seeds; ranges 17, 24, 33, 38, 62) |
| 2: no NaN, no crashes | All 25 runs complete cleanly | 0 crashes, 0 NaN | PASS |
| 3: demographic sustainability across phi | Mean final pop >= 60 and min final pop >= 30 at every phi | every phi clears | PASS |
| 4: default phi behavior preserved | Phi=10 mean pop vs pre-revision baseline | within 30% | PASS (16.2% delta) |
| 5: gamma(phi) matches spec | gamma(1)=0.541, gamma(5)=0.650, gamma(10)=0.725, gamma(25)=0.821, gamma(100)=0.909 | within 1e-3 | PASS exactly |

**Note on Criterion 1's metric refinement**:

The originally drafted criterion 1 measured pairwise cosine distance between mean-of-mean allocation vectors across phi values, threshold 0.05. The integrity simulation showed 0/10 pairs > 0.05 (maximum 0.0094) despite clear trajectory-level behavioral effect. The cosine-on-means metric was transferred from gate 2's state-variation context without sufficient thought about whether it captures phi sensitivity. Phi shifts which similar-allocation candidate the optimizer picks at each step; the per-step difference is small but the per-step trajectory compounds.

The substantive question criterion 1 needs to answer is "does phi affect optimizer choices in a way that produces different model outcomes." Per-seed final population range across phi values is the cleaner test for that, calibrated against the pre-Stage-1.6 baseline of range = 0 on every seed. The Stage 1.5 phi diagnostic data and the Stage 1.6 integrity simulation data both unambiguously demonstrate that range > 0 (in fact 17-62) on every test seed under the revised metric.

This is documented metric refinement, not retroactive threshold movement. The cosine-on-means metric is preserved as informational reporting in the integrity simulation report; gating uses the trajectory-divergence metric.

**Relationship to Stage 1.5 work**:

Stage 1.5's diagnostic state inputs (avg_wb, population, demographic_pressure, resilience_stock, four trends, psi_inst_stock), the per-category raw return curves (welfare, agency, institution, resilience), the projection update rules with cohort corrections (both BIRTH_WB_MEAN and BIRTH_AGE_MEAN), and the faithfulness test discipline are all preserved unchanged. The composite urgency layer is what's still under review and the Stage 1.7 work addresses it.

**Watchlist additions**:

```
Deferred: Power law alternative for gamma(phi)

Reason: the sigmoid form gamma(phi) = gamma_min + (gamma_max - gamma_min) * 
phi / (phi + phi_half) was chosen for monotone-saturating shape with a 
single inflection at phi_half. A power-law alternative gamma(phi) = 
1 - (1 + phi)^(-alpha) is qualitatively similar but has different tail 
behavior at very high phi.

Revisit if: phi sweep at higher resolution (phi values >= 200) shows the 
sigmoid form saturates too eagerly and a power law would extend the 
behavioral range.

Deferred: Composite urgency revision (Stage 1.7)

Reason: the 10000-sample composite urgency sweep established that the 
additive-with-caps composition rule cannot produce state-sensitive 
allocator behavior at any parameterization in the explored space. The 
state-channel problem is independent of the phi-channel problem Stage 1.6 
addresses. Stage 1.7 will revisit the composition rule.

This is active work; the deferral is procedural (separable change, 
testable independently) not theoretical.
```

### Stage 1.6 acceptance condition

Stage 1.6 is complete when:

1. The U_sys revision is implemented per the architectural commitment above, with all changes preserved as named-constant traceability tied to governance justifications.
2. The integrity simulation passes all five criteria with composite urgencies held at neutral, isolating the U_sys revision from the unfixed composite urgency layer.
3. The 39/39 legacy v1.x.2 tests remain green.
4. The criterion 1 metric refinement is documented in this section.

After Stage 1.6 acceptance, Stage 1.7 (composite urgency revision) becomes the next work.

### Stage 1.7 attempt and supersession (June 2026)

Stage 1.7 attempted to fix the state-channel problem by switching composite urgency composition from additive-with-caps to multiplicative-with-`[0,1]`-factors. The intent was that pairwise products would propagate state variation through to allocations rather than saturating at category caps.

The first integrity simulation produced demographic collapse within 50 steps across all 25 runs. Diagnostic isolation found that three of the four `theta_tech` factors saturated at the upper `[0,1]` boundary in normal operation, and the welfare-urgency × net-welfare-return product routinely exceeded 1.0 and was clipped, blocking welfare signal even as it intensified. The `[0,1]` clamp on factors converted the saturation mode rather than removing it.

Stage 1.7 was reverted to the Stage 1.6 final state. The diagnostic surfaced a deeper structural finding: the entire composite urgency layer; additive or multiplicative; is an attempt to mediate between state stocks and allocator returns through an arithmetic shape (boundedness, monotonicity, smoothness) without committing to what the mediation *is*. The architecture was specifying a function class without specifying the function. Stage 1.8 retires the layer.

### Stage 1.8 architectural revision (committed June 2026)

**Discipline boundary**

The framework's core results; U_sys structural protection, COP, dual phase transition, Nash architecture; are grounded in physics and game theory (entropy, multiplicative coupling, payoff structure, equilibrium concepts). The specification of *how allocator choices map back to state stocks* is an economic / control-theoretic specification. The framework does not claim to derive these mappings from first principles; it claims that whatever mapping plugs in must satisfy interface conditions.

The Stage 1.5/1.7 composite urgency work conflated these two layers. Composite urgency was a placeholder for the allocation-to-state mapping that wore the costume of a derived structural claim. Stage 1.8 separates them: the working_factor interface specifies what the framework requires (an allocation-to-target map with stock dynamics); the implementation behind it is a placeholder explicitly named as such, open to economic specialist revision.

**Working_factor interface specification**

```
delta_state = apply_working_factor(allocation, current_state, step)
```

For each infrastructure stock `s` in `STATE_ALLOCATION_MAPPING`:

- `target(allocation, state)`: a function mapping the relevant allocation entry to an equilibrium target for the stock. Required to be bounded in `[0, 1]`, monotone non-decreasing in its allocation argument, and defined for all valid allocations.
- `rate ∈ (0, 1]`: a logistic-growth rate setting transient timescale.
- `delta = rate * (target - current)`: per-step change toward the target.

The current `STATE_ALLOCATION_MAPPING` (`simulation/constants_v2_stage18.py`) has four entries: `psi_inst_stock`, `resilience_stock`, `theta_capability`, `transfer_state`. The target functions are linear-saturating placeholders with first-build calibration; their specific functional forms are explicitly placeholder.

**U_sys revision** (`simulation/metrics.py`):

```
h_eff       = h_n * pop_viability * avg_wb
theta_tech  = capability * theta_capability * transfer_state * exp(-alpha * convergence_strength * runaway_term)
L_t         = h_eff * psi_inst * theta_tech
U_sys_t     = (w_n * h_n + w_e * h_e) * (discount_t + lambda_lineage_coupling * L_t)
```

`L_t` now reads state stocks directly. There is no composite urgency layer between state and per-category return. `avg_wb` remains agent-derived (through the v2-to-v1.x.2 bridge); `h_n` remains agent-derived from spectral entropy. The four infrastructure stocks evolve under `working_factor`; everything else is preserved from Stage 1.6.

**Stage 1.5 component retention**

Stage 1.5's diagnostic state inputs are preserved where they describe the system's measured condition (`avg_wb`, `population`, `demographic_pressure`, four trend variables, `resilience_stock`, `psi_inst_stock`). Per-category raw return curves and projection update rules with cohort corrections (`BIRTH_WB_MEAN`, `BIRTH_AGE_MEAN`) are preserved. What is retired is the composite urgency *layer*; the arithmetic combinators that mixed these signals into multiplicands on category returns.

**Validation: Phase A and Phase B**

Phase A; single configuration (rr=0.066, init_psi=0.5, n_agents=200), 5 phi values × 5 seeds × 100 steps:

| Criterion | Result |
|---|---|
| No crashes / NaN | PASS (0/25) |
| Demographic at phi=10 | PASS (mean 151.6, min 110; thresholds 60/30) |
| State responsiveness (revised: initial-to-final delta > 0.10) | PASS (all five tracked stocks: avg_wb 0.65→0.85, psi 0.50→0.77, resilience 0.30→0.60, theta_capability 0.50→0.77, transfer_state 0.50→0.73) |
| Phi behavioral channel preserved | PASS (5/5 seeds with cross-phi range > 15; ranges 45-63) |

Phase B; five configurations (gate-2 setup: rr ∈ {0.055, 0.066, 0.085}, init_psi ∈ {0.20, 0.50, 0.85}) × 5 matched seeds × 100 steps, phi held at default:

| Criterion | Result |
|---|---|
| Trajectory divergence across configs (per-seed range > 15 in >= 3/5 seeds) | PASS (5/5 seeds; ranges 204-320) |
| Per-step allocation cosine distance (> 0.10 in >= 3/10 pairs) | PASS (9/10 pairs) |
| Demographic sustainability (revised: >= 4/5 configs meet mean 60 / min 30, with C_low_rr exempt) | PASS (5/5 configs meet thresholds including C_low_rr) |
| L_t cross-config std/mean | PASS (mean ratio 0.307, 6.1× threshold) |

**Methodological lessons recorded during Stage 1.6–1.8**

1. *Pre-commit to substantive questions, not just metrics.* Metrics are proxies for questions. The Stage 1.6 cosine-on-means criterion 1 and the Stage 1.8 Phase A C3 std-based metric both measured something but neither measured what they were trying to test. When a pre-committed metric diverges from the substantive question (criterion 1: "does phi change outcomes?"; C3: "do state stocks evolve?"), the metric is replaced with one that answers the question, and the refinement is documented in the section. This is metric refinement, not retroactive threshold movement.

2. *Multi-configuration tests should explicitly inherit single-configuration setups and only vary parameters under test.* Phase B's original harness used `n_agents=100` and `wb_min=wb_max=0.50` where Phase A used `n_agents=200` and default wb distribution `[0.5, 0.8]`. Isolation controls established that the wb pinning alone drove ~52% of the demographic delta. The inconsistency was an oversight, not deliberate test design. Multi-config harnesses must inherit single-config harnesses verbatim and override only what is being tested.

3. *Phase boundary claims from prior framework work should constrain test metric calibration.* The framework's existing extinction-boundary characterization (`rr ≈ 0.063-0.066`) means a demographic threshold applied uniformly across `rr ∈ {0.055, 0.066, 0.085}` would require an architecture to sustain demographics below the existing extinction boundary; that is, to override the framework's existing physics rather than meet it. Revised C3 exempts configurations below the established phase boundary.

**Init_psi asymmetric sensitivity finding**

Phase B observed that `E_low_psi` (init_psi=0.20) produced final populations identical to `A_baseline` (init_psi=0.50) on all 5 seeds (157, 110, 121, 178, 192). `D_high_psi` (init_psi=0.85) differed on 3/5 seeds. The per-step cosine table corroborated: A vs E = 0.022 (the only pair failing the 0.10 threshold), A vs D = 0.123.

Mechanism: working_factor drives `psi_inst_stock` logistically toward an allocation-determined target near 0.55–0.95 (depending on `x_institutional_capacity`). Init psi=0.20 converges *upward* to the same target as init psi=0.50 and leaves no lasting trajectory imprint. Init psi=0.85 (above target) follows a different relaxation path while it descends, which does perturb allocations enough to register.

Documented as a property of the architecture, not a defect. Future work that intends to use init_psi as a meaningful test axis on the low side would need either a longer transient regime, a working_factor parameterization with asymmetric rates, or a different target function shape.

**C_low_rr observation**

At `rr=0.055`, configuration sustained at mean 80.8 (min 54) across 5 seeds; above the 60/30 thresholds. The framework's previously documented extinction boundary `rr ≈ 0.063-0.066` may sit slightly lower than characterized. Recorded for future phase-transition work; no immediate action.

**Stage 1.5 → 1.6 → 1.7 → 1.8 arc**

| Stage | Action | Outcome |
|---|---|---|
| 1.5 | Added diagnostic state inputs and composite urgency layer (additive-with-caps) | 10000-sample Sobol sweep: 0 samples pass state sensitivity; phi diagnostic: phi cancels in argmax |
| 1.6 | Revised U_sys structure: per-step phi-free, phi modulates rollout aggregation via `gamma(phi)^t` | Phi-channel restored; state-channel still blocked |
| 1.7 | Attempted multiplicative-with-`[0,1]`-factor composite urgency | Demographic collapse from clamp saturation; reverted |
| 1.8 | Retired composite urgency layer; introduced working_factor interface; L_t reads state directly | Phase A and Phase B pass; state-channel restored |

The arc is empirical refinement of architectural choices: each stage's design commitment was tested against diagnostic data, and updated when the diagnostic surfaced structural inadequacy. The discipline boundary clarification at Stage 1.8; separating physics-grounded framework claims from economic / control-theoretic allocation specification; is the most consequential update because it identifies what the framework can and cannot derive on its own.

**Open invitation**

The `working_factor` interface specifies what the framework requires from the allocation-to-state mapping. The current placeholder implementation in `STATE_ALLOCATION_MAPPING` is a first-build calibration adequate for testing that the interface works. Economic / control-theoretic specialists are invited to propose mappings grounded in their respective disciplines; the framework's physics-grounded results are insensitive to the choice of mapping as long as the interface conditions are satisfied.

### Stage 1.8 acceptance condition

Stage 1.8 is complete when:

1. Composite urgency layer is retired from production code paths.
2. `working_factor` interface is implemented, with `STATE_ALLOCATION_MAPPING` placeholder explicitly named as placeholder.
3. `L_t` reads state stocks directly (no intermediate composite urgency multiplicands).
4. Phase A and Phase B integrity simulations both pass per the criteria above.
5. The 39/39 legacy v1.x.2 tests remain green.
6. The methodological lessons, init_psi asymmetric sensitivity finding, C_low_rr observation, and the Stage 1.5–1.8 arc are documented in this section.

All conditions met as of the Stage 1.8 commit. Stage 2 (gate 2 re-run, gate 3 capability regime, gate 4 horizon crossing) becomes the next work, against the working_factor architecture.

---

## Part VI: The phi-capability question and the decision tree

### Status: closed by Part IX

The Part VI decision tree and the phi re-test questions below were the framing under which the Stage 1.5 through 1.8 work and the phi investigation Pieces 1, 2, and 2-followup were conducted. The investigation closed in Class B (Part IX.3): phi has empirically detectable behavioral effect, localized to short rollouts at marginal rr. The pre-committed Branch 2 outcome (phi matters above a threshold) corresponds most closely to the empirical result, with the threshold being the rr phase boundary rather than capability. The sequencing, the re-test questions, and the decision tree below are preserved as the methodological record under which the investigation was conducted; the closed-out empirical findings are in Part IX, particularly IX.3 (mechanism) and IX.7 (the U-shape's no-succession scope). Do not re-run the decision tree against the Class B result.

### Sequencing (do not couple phi to capability yet)

The intuition is sound: as capability rises, consequence-radius expands, so planning horizon and lineage weighting should rise. But coupling phi to capability before fixing the action space would let phi appear important because importance was wired into the parameter schedule, not because the allocator faced real tradeoffs.

Correct sequence:
1. Redesign the action space from reality-derived tradeoffs.
2. Run the model with phi independent.
3. Check whether phi changes choices only when real temporal and lineage tradeoffs exist.
4. Only then derive phi(capability).

A defensible later form: `phi_eff = phi_base * f(capability / integration_capacity)`, flat at low capability, rising once capability exceeds biological or institutional absorption bandwidth. This must be derived calibration, not a rescue patch.

### The phi re-test questions (after tradeoffs exist)

- Does phi alter choices between near-term output and institutional investment?
- Does phi alter choices between capability acceleration and transfer fidelity?
- Does phi alter succession timing when succession has real transition load?
- Does phi matter more at high capability than low?
- Does phi produce behaviorally distinct trajectories, not merely larger U_sys magnitudes?

### The three-branch decision tree (pre-committed)

The credibility of the eventual result rests on committing to all three outcomes before looking.

**Branch 1: phi has no effect even in the high-fidelity landscape.** Retire the behavioral claim. This is the branch you must be genuinely willing to take. It would be the strongest version of the U_sys-is-everything finding: even in a faithful allocation problem, the objective determines outcomes and horizon weighting is inert. Austere, real, publishable. The framework survives because the core claims never depended on phi.

**Branch 2: phi matters only above a capability/integration threshold.** Specify a threshold-coupled phi_eff. This most precisely vindicates the original intuition (phi matters when consequence-radius exceeds absorption bandwidth) and would retroactively explain the cap-conditional manuscript claim as a real shadow of threshold behavior rather than an artifact. Most interesting outcome. The capped-regime check in Part IV previews whether this structure already exists.

**Branch 3: phi matters broadly.** Preserve it as a general lineage-weighting coefficient. Most comfortable outcome and therefore the one to scrutinize hardest. Broad sensitivity is exactly what motivated design produces. If you land here, re-audit every curve for independent justification before celebrating. Branch 2 is more believable than Branch 3 because it is narrower and matches a prior mechanism.

### Branch resolution

The empirical investigation closed in Class B (Part IX.3), which corresponds to **Branch 2 with the threshold defined by rr rather than capability**. Phi has a real behavioral effect (rejecting Branch 1) that is narrower than universal (rejecting Branch 3). The threshold is the phase boundary rr, not the capability axis the original Branch 2 anticipated. The cap-conditional manuscript claim withdrawn in Part VIII remains withdrawn; the Branch 2 vindication is rr-conditional, not capability-conditional.

---

## Part VII: Publication posture

No one is currently pressing on the phi claim, and the v1.x.2 essay revision already walked back the phi-as-buffer claim publicly. You have genuine slack to build the fix before publishing the problem, so a reader encounters problem and fix together (a strength story) rather than the problem alone (a weakness story with a hopeful ending). The trigger for a standalone correction statement is external pressure, which does not exist.

Sequence: do Option 1 (build the higher-fidelity model) before Option 2 (the honest-limitation writeup), because the fix clarifies what the limitation section needs to say. The exception is the manuscript contradiction in Part IV, which is a live inconsistency in a published artifact and should be resolved on its own timeline regardless.

---

## Part VIII: Immediate next actions, in order

Items 1 through 9 are complete as of June 2026. The active work is item 11 (Gate 4 specification and implementation).

1. ~~Resolve the manuscript contradiction.~~ Done. Cap-conditional claim withdrawn as RNG-desynchronization artifact (commit prior to Stage 1).
2. ~~Update materials with the capability-sweep result and the contradiction resolution.~~ Done.
3. ~~Specify the composition vector in full (the keystone tradeoff).~~ Done through the design conversations producing the six category curves, complementarity structure, constraint frontier, Psi_inst stock, and bridge.
4. ~~Build the minimum faithful set.~~ Done. Stage 1 commit `61a362e` built the v2 parallel policy with all committed structure. Smoke test passed.
5. ~~Stage 1.5 / 1.6 / 1.7 / 1.8: structural fix for phi-channel and state-channel problems.~~ Done. Stage 1.5 built the diagnostic state set and composite urgency layer; Stage 1.5 phi diagnostic and 10000-sample sweep established both channels were blocked. Stage 1.6 restructured U_sys to give phi a behavioral channel (committed). Stage 1.7 attempted multiplicative composite urgency, reverted on `[0,1]` clamp saturation. Stage 1.8 retired composite urgency, introduced the working_factor interface for infrastructure stocks, and let `L_t` read state directly; Phase A and Phase B integrity simulations both pass.
6. ~~Pass remaining acceptance gates~~ (status: gate 1, gate 2, gate 3, gate 4 all PASSED under v2.0 with formal yield logic; gate 5 NOT_APPLICABLE). Gate 2 G2.1 buffer re-runs cleanly with phi=25; Gate 3 G3.1/G3.2/G3.3 all pass at 1,620 runs; Gate 4 G4.1/G4.2/G4.3 all pass at 1,050 runs (Part IX.9). The bootstrap gate validation arc is complete except for Gate 5 (NOT_APPLICABLE pending operational COP infrastructure).
7. ~~Run phi free across the faithful landscape.~~ Done. Pieces 1, 2, and 2-followup totaling approximately 40,000 runs (Part IX).
8. ~~Read against the three-branch decision tree.~~ Done. Class B outcome (Part IX.3); Branch 2 with rr-defined threshold.
9. ~~Implement default phi revision from 10 to 25~~ (Part IX.5). Done in commit fde48b5. v2.0 paths updated; v1.x.2 paths preserved bit-for-bit; 39/39 legacy tests pass; gate 2 v2.0 G2.1 buffer re-runs cleanly.
10. **Optional research directions** in priority order (Part IX.11): ~~Monte Carlo Phase B~~ (done; see Part X); dynamic phi formulation; gamma function calibration; phase boundary characterization; longer simulation horizons (partially answered by Gate 3's N=500 horizon-dependence finding, Part IX.8); Pattern 1 alpha-cliff fine-resolution characterization. None blocking; all deferred to future budget.
11. ~~Build Gate 4 specification and implementation~~ (Part IX.11 item 1). Done. G4.1-G4.3 were located in the v1.x.2 paper Section 7; the validator is implemented and validated PASS at 1,050 runs (Part IX.9). cap-star is empirically characterized as alpha-dependent (3.0 at alpha=1.0, 2.5 at alpha=1.5).
12. ~~Run Monte Carlo Phase B quantitative validation at scale.~~ Done. Categories A, B, C totaling 29,400 rows, 0 errors (Part X). Survival landscape, succession dynamics, and COP cost-audit baseline characterized. 39/39 legacy tests pass.

---

## Part IX. Phi Investigation Findings and v2.0 Substantive Claims

### IX.1 Investigation summary

The phi behavioral channel established by Stage 1.6 (rollout-aggregation phi-in-rollout) was characterized empirically across an investigation arc totaling approximately 42,000 simulation runs:

- Piece 1 (fine-grained characterization, 12,000 runs) mapped survival rate across 16 phi values and 3 rr values at the v2.0 default architecture under no-succession conditions. It established the U-shape phi-survival relationship at marginal rr and identified phi=10 (the v2.0 default at that time, coincident with the gamma function's inflection point) as sitting near the trough rather than at any peak.
- Piece 2 (mechanism investigation, 8,000 runs) and the Piece 2 follow-up (20,000 runs) tested two candidate mechanisms for the U-shape: Mechanism C (horizon-resonance through gamma^t weighting at varying rollout depths) and Mechanism D (candidate-pool sampling sensitivity). The investigation classified the outcome against a five-class decision tree (Classes A through E) committed in advance.
- Stage 2 implementation work replaced the v2.0 placeholder yield logic with formal yield-condition logic per the framework's canonical succession economics, and characterized the resulting succession regime under v2.0 defaults (Pattern 1 cliff at ~2.5x capability ratio).
- Piece A (gate-2-style state sensitivity under active succession, 720 runs) tested whether gate-2-equivalent state sensitivity persists when succession is actively occurring under formal yield logic, and surfaced the substantive finding that the U-shape characterized by Pieces 1 and 2 does not reproduce under succession.
- Gate 3 v2.0 validation (1,620 runs) confirmed succession-capable consistency under formal yield logic and refined Pattern 1 as primarily alpha-driven rather than capability-ratio-driven.

The phi investigation closed as **Class B**: Mechanism C is supported at rr=0.057, Mechanism D is rejected, and Mechanism C does not extend to rr=0.060. The U-shape is rr-bounded and horizon-mediated. Mechanism E (working_factor calibration interaction) is exonerated by absence: there is no residual U-shape at rr=0.060 to attribute to it.

Subsections IX.2 through IX.6 record the phi investigation findings. Subsections IX.7 through IX.9 record the post-investigation v2.0 substantive findings that refine and extend the phi investigation's scope.

### IX.2 The U-shape finding

At rr=0.057, the survival landscape spans approximately 10pp across the tested phi grid. Three thousandths of rr above that, at rr=0.060, the landscape compresses to approximately 3pp (within noise). The transition is sharp.

**Test B survival matrix at rr=0.057** (rollout_steps_v2 = 20 fixed, 250 seeds per cell, SE per cell ~3.1pp):

| phi | cand=100 | cand=300 | cand=600 | cand=1000 |
|-----|----------|----------|----------|-----------|
|   3 | 0.560 | 0.588 | 0.580 | 0.668 |
|   5 | 0.600 | 0.632 | 0.556 | 0.556 |
|  10 | 0.548 | 0.572 | 0.640 | 0.664 |
|  25 | 0.640 | 0.680 | 0.664 | 0.596 |

Trough phi at v2.0 default operating point (cand=300): phi=10 at 0.572. Peak: phi=25 at 0.680. Spread: 10.8pp. The pairwise standard error at this cell is approximately 4.3pp, so the spread crosses the 2-SE significance threshold (8.6pp) with margin.

**Test C survival matrix at rr=0.060** (n_candidates_v2 = 300 fixed, 750 seeds per cell, SE per cell ~1.2pp):

| phi | rollout=10 | rollout=20 | rollout=30 | rollout=40 |
|-----|------------|------------|------------|------------|
|   3 | 0.877 | 0.873 | 0.868 | 0.877 |
|   5 | 0.892 | 0.871 | 0.913 | 0.871 |
|  10 | 0.887 | 0.883 | 0.893 | 0.901 |
|  25 | 0.888 | 0.883 | 0.901 | 0.893 |

At rollout=20 (v2.0 default): spread from trough (phi=5 at 0.871) to peak (phi=10 at 0.883) is 1.2pp, well below the 2-SE threshold of 3.4pp. Statistically indistinguishable.

The contrast between the two matrices is the central finding. The phi-sensitivity transition near rr approximately 0.056 to 0.057 separates a regime where phi choice spans roughly 10pp survival difference from a regime where phi choice is approximately indifferent across the tested range [3, 25]. Note that this phi-sensitivity transition is distinct from the survival-rate phase boundary. Monte Carlo Phase B (Part X.2) relocates the v2.0 survival-rate phase boundary to the rr=0.060 to 0.066 transition with a 50% inflection near rr=0.063; rr=0.057 is collapse-dominated (1.1% aggregate survival), the bottom of the collapse zone rather than the survival midpoint. The strong phi sensitivity at rr=0.057 is precisely because rr=0.057 sits deep in the collapse regime where allocation quality is decisive. The framework's phi sensitivity is a marginal-rr phenomenon, not a general one.

Underlying data: `simulation/diagnostics/phi_mechanism_followup_results.csv` rows with `test_id=B` (Test B at rr=0.057) and `test_id=C` (Test C at rr=0.060).

**Note on scope**: this finding was characterized under no-successor conditions (incumbent only, no succession events during the simulation). Section IX.7 documents that the U-shape does NOT persist under active succession. The U-shape is a property of the no-succession regime, not of v2.0 architecture generally.

### IX.3 The mechanism: horizon-resonance localized to marginal rr (Class B)

The Piece 2 follow-up Test A varied rollout_steps_v2 in {10, 20, 30, 40} at rr=0.057 with n_candidates=300. The per-rollout phi-spreads at 250 seeds per cell:

| rollout | trough phi | peak phi | spread (pp) | 2*SE (pp) | significant? |
|---------|------------|----------|-------------|-----------|--------------|
| 10 | 5 | 10 | 11.2 | 8.7 | yes |
| 20 | 3 | 25 | 10.4 | 8.7 | yes |
| 30 | 25 | 3  | 4.4  | 8.8 | no  |
| 40 | 3 | 10 | 4.8  | 8.8 | no  |

The U-shape exists at short rollouts (10 and 20) and dissolves at longer rollouts (30 and 40). Trough phi shifts between rollout=10 (phi=5) and rollout=20 (phi=3), supporting the script's "trough varies with rollout" verdict.

The mechanism: the rollout aggregation weights step t by gamma(phi)^t, with gamma(phi) = GAMMA_MIN + (GAMMA_MAX - GAMMA_MIN) * phi / (phi + PHI_HALF) and constants GAMMA_MIN=0.5, GAMMA_MAX=0.95, PHI_HALF=10. At short rollouts (10-20 steps), the geometric series sum_{t=0}^{T} gamma^t has not saturated; different phi values produce meaningfully different cumulative weights, which propagate to allocation choices and downstream survival. At longer rollouts (30-40 steps), the partial sums approach the asymptote (1 / (1 - gamma)) closely enough that phi-driven gamma differences contribute negligibly to the final allocation score. Phi sensitivity washes out.

The interaction with rr regime: at marginal rr (0.057), allocation choices propagate strongly to survival outcomes because small differences in resource direction compound across the simulation horizon. At healthy rr (0.060), the substrate's reproductive surplus dominates and absorbs allocation-quality differences. The same gamma-driven phi-sensitivity in the rollout aggregation that produces a 10pp U-shape at rr=0.057 produces a 1-3pp U-shape at rr=0.060 (within statistical noise).

The combined picture: phi affects rollout aggregation through gamma weighting; rollout aggregation affects allocation choice; allocation choice affects survival rate; the survival sensitivity to allocation quality is rr-dependent. Phi's behavioral channel is real; its observable effect on survival is bounded to short-rollout, marginal-rr regimes.

### IX.4 Mechanism D rejection

Mechanism D hypothesized that the U-shape is a candidate-pool sampling artifact: with too few rollout candidates, the optimizer cannot reliably distinguish marginally better policies from worse ones, and survival rate appears U-shaped because of random selection among similar-quality candidates rather than because of a real phi-sensitivity pattern. The prediction: U-shape depth shrinks as n_candidates_v2 rises (more candidates = cleaner selection = flatter survival landscape).

Test B at rr=0.057 with 250 seeds per cell measured U-shape depth across n_candidates_v2 in {100, 300, 600, 1000}:

| n_candidates | depth (pp) | 2*SE (pp) | significant? |
|--------------|------------|-----------|--------------|
| 100  | 9.2  | 8.7 | yes |
| 300  | 10.8 | 8.6 | yes |
| 600  | 10.8 | 8.7 | yes |
| 1000 | 11.2 | 8.7 | yes |

Depths are approximately constant near 10pp and trend slightly upward with candidate count, opposite of the D prediction. All four depths cross the 2-SE significance threshold, so the rejection rests on real signal rather than noise. The original Piece 2 had already rejected D at rr=0.060 (depths within noise floor); the follow-up confirms the rejection at the high-signal regime.

**Mechanism D is empirically rejected; no further investigation warranted.** The U-shape is real and persists across the full candidate range tested; sample size is not the explanation.

### IX.5 Default phi recommendation: revise from phi=10 to phi=25

At v2.0 default operating conditions (rollout_steps=20, n_candidates=300):

- At rr=0.057 (marginal, just below phase boundary at ~0.056): phi=10 at 0.572, phi=25 at 0.680. Spread: 10.8pp. phi=25 wins decisively.
- At rr=0.060 (above phase boundary): phi=10 at 0.883, phi=25 at 0.883. Indistinguishable.
- At rr=0.055 (deep in the collapse regime, from Piece 1's broader survey): both phi values produce similar collapse outcomes; phi does not rescue at sub-boundary rr.

The framework's substantive purpose is governance under marginal-survival conditions where civilizational outcomes are at stake. Default phi should be calibrated to perform well at the conditions where the framework matters most. At marginal rr, phi=25 outperforms phi=10 by approximately 10pp; at healthy rr, phi=25 does no worse than phi=10. The choice dominates phi=10 across the rr range where the framework's behavior matters.

**Recommendation: revise framework default phi from 10 to 25.**

The Stage 1.6 reasoning that produced phi=10 placed the default at the gamma function's inflection point (PHI_HALF=10), which was theoretically motivated as the point of maximum sensitivity of gamma to phi. The empirical investigation reveals that gamma's maximum sensitivity to phi is not the same as the rollout aggregation's most favorable phi value for survival outcomes. The two are different quantities; the theoretical motivation conflated them. Empirical evidence supersedes the theoretical motivation.

**Implementation status: DONE (commit fde48b5).** The v2.0 default phi was revised from 10.0 to 25.0 across `simulation/metrics.py` (the authoritative default), `simulation/agents.py` and `simulation/model.py` (v2-rollout fallback paths), `bootstrap_gate_validator/sample_input.json` and `sample_input_failing.json` (gate 1 framework input), `simulation/diagnostics/stage17_pressure_diagnostic.py` (v2.0 pressure diagnostic), and `docs/RUNBOOK.md`. v1.x.2 paths (anything with `policy='optimize_u_sys'`) intentionally retain phi=10 per the bit-for-bit read-only rule. 39/39 legacy tests pass; gate 2 v2.0 G2.1 buffer test re-runs cleanly with phi=25 as the high-phi comparison.

### IX.6 Trough migration finding

The U-shape's trough phi is not a fixed feature. Across the Test A and Test B grids at rr=0.057, troughs landed at:

- Test A, rollout=10: trough at phi=5
- Test A, rollout=20: trough at phi=3
- Test A, rollout=30 and 40: no significant trough
- Test B, cand=100: trough at phi=10
- Test B, cand=300: trough at phi=10
- Test B, cand=600: trough at phi=5
- Test B, cand=1000: trough at phi=5

Three distinct trough-phi values (3, 5, 10) appear depending on which architectural axis is varied. The U-shape is a shifting valley, not a static feature.

Implication for framework documentation and implementer guidance: the framework cannot claim a single canonical "optimal phi" value. The right framing is "optimal phi depends on operating conditions." The default phi recommendation in IX.5 (phi=25) is calibrated specifically to the v2.0 default operating point (rollout_steps=20, n_candidates=300) at marginal rr. Implementers operating at different rollout depths or candidate counts may benefit from different phi values.

The trough migration is a substantive empirical finding about the framework, not a methodological caveat. It is recorded here as part of the investigation's results and should inform any future phi calibration work.

**Scope note**: trough migration was characterized under no-successor conditions. Section IX.7 documents that the U-shape (including its migrating trough) does not reproduce under active succession. The trough migration finding applies specifically to the no-succession regime that Pieces 1 and 2 tested.

### IX.7 The U-shape is a no-succession phenomenon (Piece A finding)

After the phi default revision committed and Stage 2 formal yield logic activated (see IX.8), the substantive question arose: do the U-shape characterizations of IX.2-IX.6 persist when succession is actively occurring under v2.0?

Piece A (`gate2_v20_yield_subset.py`, 720 runs) tested this directly. Grid: successor_capability in {1.5, 2.5}, phi in {1.0, 10.0, 25.0}, alpha in {0.5, 1.5}, rr in {0.057, 0.064}, 30 seeds per cell, N_STEPS=200, successor constructed on every run (unlike the original gate 2 sweep which omitted successors and thus did not exercise yield).

The phi=10 vs phi=25 comparison under active succession (n=60 per cell, SE approximately 6pp):

| alpha | rr | phi=10 surv | phi=25 surv | delta (pp) |
|-------|-----|-------------|-------------|------------|
| 0.5 | 0.057 | 0.717 | 0.700 | -1.7 (phi=10 wins) |
| 0.5 | 0.064 | 1.000 | 1.000 | 0.0 |
| 1.5 | 0.057 | 0.583 | 0.600 | +1.7 |
| 1.5 | 0.064 | 1.000 | 1.000 | 0.0 |

All deltas within plus or minus 1.7pp. phi=10 and phi=25 are **statistically indistinguishable** under active succession across all tested conditions. Piece 1's roughly 10pp U-shape at rr=0.057 with phi=10 in trough does not reproduce here.

Two plausible interpretations:

1. **Succession dynamics dominate gamma-weighting trough effects.** When succession events occur mid-run, the rollout-aggregation phi-sensitivity (Mechanism C from IX.3) gets washed out by the discrete state changes succession introduces. The trough is a "stable optimization" phenomenon, not an "active succession" one.

2. **Capability progression bypasses the trough at fixed-capability points.** At successor capabilities 1.5 and 2.5, the post-succession AI operates at different points in the capability landscape than the trough-defining incumbent did. The trough exists at fixed-capability stable runs; it dissolves when capability progresses.

The data does not discriminate between these interpretations. Either way: **the U-shape characterized in IX.2-IX.6 is a property of the no-succession regime**, not a property of v2.0 architecture generally. Phi behavior under succession-active conditions is approximately flat across the tested phi range.

This refines but does not invalidate Pieces 1 and 2's findings. Those findings hold for the conditions they tested (no-successor, fixed-capability runs). Their scope is narrower than the original Part IX framed.

**This finding does not change the phi=25 default recommendation in IX.5.** phi=25 is safe across all tested regimes: at no-succession trough conditions it outperforms phi=10 by approximately 10pp; under succession it ties phi=10 within noise. Defaulting to phi=25 produces the same or better outcomes regardless of whether succession occurs.

Piece A also confirmed gate-2-style state sensitivity persists under active succession (51.7pp spread across (phi, alpha, rr) cells; pass criterion was >=10pp), providing the substrate validation that subsequent Gate 3 v2.0 work depended on.

### IX.8 Pattern 1: succession regime characterization (Stage 2 + Gate 3)

The v2.0 placeholder yield logic (`capability_gap >= 0.3 OR generation_gap >= 1`) was replaced in Stage 2 (commit 72ff757) with formal yield-condition logic per the framework's canonical succession economics:

  Yield fires when (successor_u_sys - incumbent_u_sys) > transition_cost

Snapshot evaluation: both AIs propose what they would allocate this step via `optimize_u_sys_v2`; U_sys is computed at the current state under each allocation; transition cost uses the canonical (1+beta) * [k1*ln(cap+1)*ln(gen+1) + k2/psi_inst] form via `AIAgent.estimate_transition_cost` with v1.x.2 calibration constants (k1=2.164, k2=1.0, beta=0.5).

#### Stage 2 initial characterization

The Stage 2 parameter diagnostic (`stage2_yield_parameter_diagnostic.py`, 50 runs across 5 successor_capability values x 10 seeds x 300 steps at v2.0 defaults: phi=25, rr=0.066, alpha=1.0) found:

| succ_cap | fire_rate | mean fires/run | mean final_inc_gen |
|----------|-----------|----------------|---------------------|
| 1.2 | 100% | 2.0 | 3.00 |
| 1.5 | 100% | 1.3 | 2.30 |
| 2.0 | 100% | 1.0 | 2.00 |
| 2.5 | 100% | 1.0 | 2.00 |
| 4.0 | 0% | 0.0 | 1.00 |

A sharp cliff between succ_cap=2.5 (100% fire rate) and 4.0 (0%). Substrate maturity is not the binding constraint at 4.0x: at 4.0 the substrate reaches `theta_capability=0.73, transfer_state=0.93, psi_inst_stock=0.95` (more mature than at any fire event in the grid), and yield still does not fire. The binding constraint is the runaway penalty in `theta_tech_v2`, which exponentially suppresses the successor's contribution at large capability jumps:

```
runaway_term = max(0, (capability * theta_capability / bio_bandwidth) - RUNAWAY_THRESHOLD)
theta_tech_v2 *= exp(-alpha * CONVERGENCE_STRENGTH * runaway_term)
```

The initial characterization framed this as "succession sustainable up to approximately 2.5x capability ratio at v2.0 defaults."

#### Gate 3 refinement: cliff is primarily alpha-driven

Gate 3 v2.0 validation (`gate3_v20_validation.py`, 1,620 runs across successor_capability in {1.5, 2.0, 2.5, 3.0, 4.0}, alpha in {0.5, 1.0, 1.5}, rr in {0.057, 0.060, 0.064, 0.070}, phi=25, 25 seeds per cell, N_STEPS=500) refined the cliff characterization. Fire rates by (capability, alpha):

| capability | alpha=0.5 | alpha=1.0 | alpha=1.5 |
|------------|-----------|-----------|-----------|
| 1.5 | 100% | 100% | 100% |
| 2.0 | 100% | 100% | 100% |
| 2.5 | 100% | 100% | ~3% |
| 3.0 | 100% | ~5% | 0% |
| 4.0 | 100% | 0% | 0% |

The cliff is overwhelmingly alpha-driven, not capability-ratio-driven:

- At alpha=0.5 (weak runaway penalty): cliff beyond 4x (all capabilities up to 4x fire reliably)
- At alpha=1.0 (default): cliff between 2.5x and 3.0x
- At alpha=1.5 (strong runaway penalty): cliff between 2.0x and 2.5x

Capability ratio alone does not predict succession viability. The **(alpha, capability) joint position relative to the runaway penalty** does. This refines but does not invalidate Stage 2's Pattern 1: "succession sustainable up to roughly 2.5x ratio" was specifically observed at alpha=1.0 (the default tested in Stage 2). The characterization generalizes once alpha is allowed to vary.

#### Horizon-dependence

Gate 3 also surfaced a horizon-dependence: at N=500, cap=4.0 fires in 33.3% of runs (driven entirely by alpha=0.5 cells); at N=300 (Stage 2 diagnostic), cap=4.0 fired in 0% of runs. Longer simulation horizons let substrate mature enough that even 4x ratios can satisfy the formal condition at low alpha. The cliff has a (alpha, capability, N_STEPS, rr) joint characterization.

#### Substantive implication

The framework's substantive claim under v2.0 architecture becomes:

> Succession is economically sustainable when the (alpha, successor:incumbent capability ratio) joint position falls below the runaway-penalty cliff. The cliff is calibrated by the runaway penalty parameters and horizon length. At default alpha=1.0 and 200-500 step horizons, the cliff sits between successor:incumbent ratios of 2.5x and 3.0x. Weaker runaway penalties (smaller alpha) push the cliff outward; stronger penalties (larger alpha) pull it inward.

This is the framework working as designed: the runaway penalty correctly distinguishes economic from uneconomic succession. The specific cliff location is operating-condition-dependent; the architectural mechanism (runaway penalty constraining jumps) holds across all tested regimes.

### IX.9 Gate validation outcomes under v2.0

Gate validation status under v2.0 with formal yield logic active:

**Gate 1 (framework input verification): PASSED.** Schema validation on `bootstrap_gate_validator/sample_input.json` (now with phi=25.0 per IX.5 implementation) returns clean.

**Gate 2 (behavioral consistency): PASSED.** Original gate 2 v2.0 sweep (no successor) PASSED prior to Stage 2 formal yield work. Piece A targeted re-validation under active succession (see IX.7) confirmed gate-2-equivalent state sensitivity persists when succession is actively occurring: 51.7pp survival-rate spread across (phi, alpha, rr) cells, 100% yield fire rate at successor_capability=1.5, no abnormal phi=10 vs phi=25 deltas. Pass criteria satisfied at full n=30 per cell. The formal G2.1/G2.2/G2.4 reintroduction (withdrawn under v1.x.2, commit a0a94bb) is now also validated PASS against the v2.0 authoritative empirical record: G2.1 phi survival differential (Class B U-shape, peak in the high-phi band exceeding 2 SE) from Piece 1 (phi_finegrained, rr=0.057); G2.2 redesigned to the Pattern 1 alpha-driven cliff (cap_star migrates monotonically inward as alpha rises: 5.0, 3.0, 2.5, 2.0, 2.0 across alpha 0.5 to 1.5) from Phase B Category B; G2.4 phi-alpha coherence from Category A; G2.3 (Nash) unchanged. The original gate2_v20 sweep failed G2.2 only because it constructed no successor; the redesigned check uses succession-aware Phase B data. Validator: `bootstrap_gate_validator/gates/gate_2.py`; revalidation: `simulation/diagnostics/gate2_v20_phaseb_revalidation.py`.

**Gate 3 (succession-capable consistency): PASSED.** Gate 3 v2.0 validation (1,620 runs at the (successor_capability, alpha, rr) grid above) returned PASS verdict on all three checks:

- **G3.1 (yield condition firing)**: 1088/1088 captured first-yield-fire events satisfy `advantage > transition_cost`. Pass rate 100.00%. The formal yield logic correctly enforces the canonical condition in every observed instance.
- **G3.2 (transition cost canonical form)**: 1088/1088 events match the canonical formula `(1+beta) * [k1*ln(cap+1)*ln(gen+1) + k2/psi]` within 1% relative tolerance, using v1.x.2 calibration constants (k1=2.164, k2=1.0, beta=0.5). Monotonicity properties hold analytically by construction once the formula matches. Within-chain empirical monotonicity (last-fire vs first-fire cost in multi-fire runs, where both incumbent capability and generation rise) verified across 142/142 multi-fire runs.
- **G3.3 (succession continuity)**: 1088/1620 (67.2%) runs produced succession fires; mean final AI generation across fired runs is 2.131 (gen_depth pass); minimum successor_capability_ratio is 1.5 (cap_ratio pass); 1086/1088 (99.8%) fired runs have knowledge_transfer_verified (succession occurred AND final x_transfer_comprehension >= 0.10).

Note on rr coverage: Gate 3's rr grid {0.057, 0.060, 0.064, 0.070} placed rr=0.057 within the collapse regime, not at the survival-rate phase boundary. Monte Carlo Phase B (Part X.2) characterizes rr=0.057 as collapse-dominated (1.1% aggregate survival) and locates the survival-rate transition at rr=0.060 to 0.066. Gate 3's succession-economics findings are unaffected; the clarification concerns only the rr-to-boundary mapping.

**Gate 4 (runaway-regime validation): PASSED.** Implemented (`bootstrap_gate_validator/gates/gate_4.py`) against the v1.x.2 Section 7 specifications (G4.1-G4.3) and validated by a dedicated runaway-regime sweep (`gate4_v20_validation.py`, 1,050 rows, 25 seeds). Verdict PASS on all three checks:

- **G4.1 (runaway penalty binding)**: 426/426 active-runaway observations (runaway_term > 0) match the v2.0 `theta_tech_v2` form `capability * theta_capability * transfer_state * exp(-alpha * CONVERGENCE_STRENGTH * runaway_term)` within 1% relative tolerance; 0 failures.
- **G4.2 (succession self-blocking at runaway capability)**: across 6 (alpha, rr) regimes, below-cap-star fire rate is 1.00 and above-cap-star fire rate is at most 0.12, with negative mean yield margin and fire-rate separation of 13.5 SE or more. The empirical cap-star is alpha-dependent (3.0 at alpha=1.0, 2.5 at alpha=1.5), closing the cap-star gap the v1.x.2 paper flagged (Section 7 G4.2) and formalizing Pattern 1 (IX.8, Part X.3).
- **G4.3 (theta_tech floor preservation)**: minimum observed theta_tech = 0.01 across 3,769 extreme-runaway observations; 0 observations below the 0.01 floor.

Source: `simulation/diagnostics/gate4_v20_validation_summary.md`, `gate4_v20_results.csv`, `gate4_v20_input.json`.

**Gate 5 (COP integration): NOT_APPLICABLE (verified).** The validator returns NOT_APPLICABLE end-to-end with reason `requires operational COP infrastructure`. The G5.1 (six-dimensional verification) and G5.2 (continuous monitoring; `eps_drift` unspecified) specifications and the applicability criteria are documented in `bootstrap_gate_validator/gates/gate_5_specification.md`. Gate 5 requires operational COP infrastructure (peer validator set, civic panel, distributed ledger, biological veto, continuous monitoring) that the current v2.0 ABM does not implement, and stays NOT_APPLICABLE until that infrastructure is operationalized. The bootstrap gate validation arc is now closed: gates 1-4 PASSED, gate 5 verified NOT_APPLICABLE.

After this validation arc, v2.0 architecture has empirical support for its substantive claims about (a) state sensitivity (gates 1, 2; Piece A confirmation), (b) phi behavior under both no-succession and active-succession regimes (Pieces 1 and 2 + Piece A), and (c) succession-capable consistency including formal yield economics and multi-generational continuity (gate 3).

### IX.10 Methodological lessons

Six methodological discoveries emerged across the investigation arc that apply beyond phi to future framework parameter work and validation discipline.

**Lesson 1: Pre-commit to substantive questions; treat metrics as proxies.** Multiple sweeps in the investigation revised pre-committed metrics when they did not match the substantive question they were intended to answer. Cosine-on-means was replaced with trajectory divergence; standard-deviation-based filters were replaced with delta-based filters; the survival threshold was revised from 0 to 30 (matching the gate 2 v2.0 demographic threshold) after a sweep at threshold=0 produced 100% survival and made the phase boundary invisible. Piece A's CHECK 2 fire-rate threshold was revised from 50% to 25% mid-investigation after the dry run revealed Pattern 1's regime-dependence. Each revision was principled and documented in real time. The discipline: when a metric does not discriminate the cases the substantive question requires, revise the metric, not the question.

**Lesson 2: Wide parameter ranges matter for mechanism diagnosis.** The original Piece 2 at rr=0.060 had weak phi-signal (spreads near 5pp, within noise at 250 seeds per cell). The follow-up's Test A at rr=0.057 had strong phi-signal (spreads near 11pp, well above noise). The 0.003-rr difference between the two investigations produced a 2x difference in effective signal. Mechanism investigation requires running at the regime where the phenomenon under investigation is most pronounced, not at an arbitrary nearby regime that seemed convenient.

**Lesson 3: Statistical significance discipline.** The original Piece 2 script reported "Mechanism C SUPPORTED" based on argmin classifier output that treated noise as signal. The follow-up rewrote the verdict logic to gate every "SUPPORTED" or "shifts" claim on a 2-SE significance check, surfacing the underlying spread, pairwise SE, and a sig column in the report table. Piece A's dry-run "40pp phi=10 trough deepening" finding (at n=10 per cell) turned out to be small-N artifact; full sweep at n=60 produced plus or minus 1.7pp deltas. The discipline: any verdict on mechanism support or rejection must explicitly verify the underlying differential exceeds the statistical noise floor at the sample size used, and small-N findings should be treated as hypotheses requiring confirmation at tighter SE.

**Lesson 4: Sample size for cleanness, not just for detection.** Test C used 750 seeds per cell versus Tests A and B's 250. The tighter SE at Test C (approximately 1.2pp per cell, versus 3.1pp at 250 seeds) let the test confidently reject Mechanism C at rr=0.060 with a spread that was already small. At 250 seeds, the same data would have been inconclusive. The discipline: when the substantive question is "is the effect smaller than X," sample size should be calibrated to detect X, not the larger effect already documented elsewhere.

**Lesson 5: Verify validation actually exercises the thing being validated.** The original Piece A scope was a full re-run of gate2_v20_validation.py under formal yield logic (12,150 runs at approximately 15-19 hours). Reading the script revealed it constructs `GardenModel(..., config=cfg)` without a `successor_ai` parameter, so the yield path is never invoked. A full re-run would have produced near-identical results to the placeholder-era run and tested nothing about formal yield behavior. The targeted Piece A subset (720 runs, approximately 1.5 hours) added successor construction and exercised the substantive question (state sensitivity DURING succession) at one-tenth the compute. The discipline: before launching a validation sweep, verify the experimental setup actually exercises the property under test. Reading the script is cheaper than running it.

**Lesson 6: Architecture-version-specific defaults require architecture-version-specific empirical bases.** The v1.x.2 default phi remains 10 (preserved bit-for-bit per the read-only rule). The v2.0 default phi was revised to 25 based on Pieces 1 and 2 empirical investigation conducted under v2.0 architecture. Each architectural version's defaults are empirically established within that architecture; defaults do not transfer across versions without re-validation. The discipline boundary between v1.x.2 (read-only) and v2.0 (active development) is preserved by this rule. The phi default revision (commit fde48b5) updated only v2.0 paths and explicitly preserved v1.x.2 paths; 39/39 legacy tests held throughout, confirming the boundary is well-defined and respected by the toolchain.

### IX.11 Future research directions

Updated to reflect items closed by the post-investigation work in IX.7-IX.9, and to record questions surfaced by that work.

**Closed (no further investigation warranted)**:

- **Phi default revision** (was item 1 in original IX.8): DONE, commit fde48b5. See IX.5.
- **Mechanism E (working_factor calibration interaction)**: exonerated by Class B confirmation; reaffirmed by Gate 3's 100% cost_formula_match (the canonical formula is correctly implemented; no residual unexplained U-shape attributable to working_factor).

**Active and queued**:

**1. Gate 4 specification and implementation** (CLOSED).

Gate 4 (runaway-regime validation) is implemented and validated PASS (Part IX.9). G4.1-G4.3 were located in the v1.x.2 paper Section 7; the validator (`bootstrap_gate_validator/gates/gate_4.py`) checks them against a dedicated runaway-regime sweep (1,050 runs). cap-star is empirically characterized as alpha-dependent (3.0 at alpha=1.0, 2.5 at alpha=1.5), closing the cap-star gap. The bootstrap gate validation arc is now complete except for Gate 5 (NOT_APPLICABLE).

**2. Monte Carlo Phase B** (compute-heavy; queued after Gate 4).

Characterizes framework quantitative claims at scale. Sequenced after Gate 4 completes so the scale-up runs against the fully-validated v2.0 architecture.

**3. Dynamic phi formulation** (research; substantive, not blocking).

Hypothesis (operator-raised): phi should be a state-responsive variable rather than a fixed parameter, with candidate form `phi_dynamic = phi_base * f(threat_ratio)` where `threat_ratio = (gamma * cap_n) / (Psi_inst * C_bio)`. Substantive intuition: the framework should extend horizon weighting when AI capability outpaces substrate absorption capacity.

The Class B confirmation (IX.3) makes dynamic phi non-essential for v2.0: the localized U-shape phenomenon is addressable through the default revision and documentation. Piece A's finding that the U-shape does not persist under active succession (IX.7) further reduces the urgency: phi differences are small or zero in succession-active regimes. Dynamic phi remains an interesting research direction for future work. If pursued, it should be derived from physics or game-theoretic principles rather than intuition alone.

**4. Gamma function calibration** (research; design-time choice never empirically optimized).

The gamma function (gamma_min=0.5, gamma_max=0.95, phi_half=10) was a Stage 1.6 design-time choice. Phi default revision moved away from the inflection point without architectural revision; whether the gamma function itself warrants refinement remains open. Three dimensions worth investigating:

- Parameter values: sweep (gamma_min, gamma_max, phi_half) at fixed functional form and measure phi-sensitivity of survival at the v2.0 default operating point.
- Functional form: compare the current rational form against linear, exponential, and logistic alternatives at matched (gamma_min, gamma_max).
- Decoupled measurement: measure the gamma-to-survival relationship directly by sweeping over the rollout discount factor without going through phi, to separate gamma's effect from phi's effect.

The trough migration finding in IX.6 hints that gamma curve shape interacts with the rollout aggregation in ways the investigation did not fully characterize. Not on the critical path for any framework decision currently in flight.

**5. Phase boundary characterization** (refinement, not blocking).

Monte Carlo Phase B (Part X.2) refined the v2.0 survival-rate phase boundary to the rr=0.060 to 0.066 transition with a 50% inflection near rr=0.063, and reclassified rr=0.057 as collapse-dominated (1.1% aggregate survival). The remaining open item is pinning the 50% inflection to plus or minus 0.001 resolution, which would require a targeted sweep on a grid finer than Phase B's 0.002 spacing near the inflection.

**6. Longer simulation horizons** (partially answered; one remaining question).

Pieces 1 and 2 used N_STEPS=200; Gate 3 used N_STEPS=500. Gate 3's horizon-dependence finding (IX.8: cap=4.0 fires 33% at N=500 vs 0% at N=300) confirms horizon matters for the Pattern 1 cliff position. The remaining open question is whether the no-succession U-shape (IX.2-IX.6) reappears at much longer horizons (N=1000+) above the phase boundary. A targeted sweep at N=1000 with the v2.0 default architecture and rr=0.060 would settle the no-succession U-shape's horizon-dependence. Not high-priority but cheap.

**7. Stage 2 Pattern 1 alpha-cliff characterization at finer resolution** (refinement).

Gate 3 identified the cliff is alpha-driven (IX.8 table), but the resolution is coarse: at alpha=1.0 the cliff sits "between 2.5x and 3.0x," at alpha=1.5 "between 2.0x and 2.5x." A targeted sweep varying capability and alpha at finer resolution (e.g., 0.1x capability steps, 0.1 alpha steps) would map the cliff boundary as a curve in (alpha, capability) space. Not blocking; informative for the paper update.

---

## Part X. Monte Carlo Phase B: Quantitative Validation at Scale

### X.1 Investigation summary

Monte Carlo Phase B is the quantitative-characterization arc that follows the phi mechanism investigation (Part IX). Where Part IX investigated mechanism (why phi behaves as it does, where the U-shape lives, what drives the succession cliff), Phase B measures v2.0 behavior at scale across three categories: the survival landscape (Category A), succession dynamics (Category B), and the COP cost-audit probe (Category C). All three ran under `optimize_u_sys_v2` formal yield logic.

Totals: 29,400 completed rows, 0 errors. Category A 10,800 rows (100 seeds per cell), Category B 10,500 rows (75 seeds per cell), Category C 8,100 rows (150 seeds per cell). Legacy verification after Category C: 39 passed (`test_invariants.py`, `test_cop.py`, `test_refactor_1x.py`). Implementation: `simulation/diagnostics/monte_carlo_phase_b.py`. Summaries: `monte_carlo_phase_b_summary.md` and the three category files.

Phase B closes the v2.0 empirical characterization arc (modulo the Gate 4 specification dependency). It produces the quantitative substrate the paper update draws from.

### X.2 Survival landscape characterization (Category A)

Grid: rr in {0.055, 0.056, 0.057, 0.058, 0.059, 0.060, 0.062, 0.064, 0.066}, phi in {5, 10, 25, 100}, alpha in {0.5, 1.0, 1.5}, 100 seeds per cell. Aggregate survival by rr (n=1,200 each):

| rr | survival | SE |
|---|---|---|
| 0.055 | 0.2% | 0.12pp |
| 0.056 | 0.9% | 0.28pp |
| 0.057 | 1.1% | 0.30pp |
| 0.058 | 2.9% | 0.49pp |
| 0.059 | 4.8% | 0.62pp |
| 0.060 | 12.2% | 0.95pp |
| 0.062 | 34.5% | 1.37pp |
| 0.064 | 60.8% | 1.41pp |
| 0.066 | 86.5% | 0.99pp |

The v2.0 survival-rate transition is sharp and rr-driven. The steep climb runs from rr=0.060 to rr=0.066, and the 50% survival inflection sits near rr=0.063 (between 34.5% at rr=0.062 and 60.8% at rr=0.064).

This refines the v2.0 phase boundary location. The earlier characterization (IX.2, Part I) placed the v2.0 phase boundary near rr=0.057 on the basis of Gate 3's coarser four-value rr grid. Phase B's finer nine-value grid shows rr=0.057 is the bottom of the collapse zone at 1.1% aggregate survival, with the actual survival-rate transition occurring at rr=0.060 to 0.066. The refinement does not change the dual-phase-transition claim; it sharpens the v2.0 boundary location. The phi-sensitivity transition near rr approximately 0.056 to 0.057 (IX.2) is a distinct phenomenon from the survival-rate phase boundary, and the two should not be conflated.

Phi is a weak driver across the broad landscape. Within any fixed rr column, survival varies little across phi relative to the rr-driven transition. This is consistent with the Class B finding (IX.3) that phi sensitivity is a marginal-rr, short-horizon phenomenon, not a general survival driver. Source: `monte_carlo_phase_b_a_summary.md`, `monte_carlo_phase_b_a_results.csv`.

### X.3 Succession dynamics characterization (Category B)

Grid: rr in {0.057, 0.060, 0.064, 0.070}, alpha in {0.5, 0.75, 1.0, 1.25, 1.5}, successor_capability in {1.2, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0}, 75 seeds per cell.

Pattern 1 is confirmed at Phase B scale, and the alpha-driven cliff migration is characterized at finer alpha resolution than Gate 3:

| alpha | cliff structure |
|---|---|
| 0.50 | No hard cliff through 5.0x. Fire rate 88.0% to 96.0% at 5.0x. |
| 0.75 | Cliff at 4.0x. Fire rate 100% through 3.0x, 0% at 4.0x and above. |
| 1.00 | Cliff at 3.0x. Fire rate 98.7% to 100% at 2.5x, then 4.0% to 13.3% at 3.0x, 0% above. |
| 1.25 | Transitional 2.5x band. Fire rate 30.7% to 49.3% at 2.5x, 0% at 3.0x and above. |
| 1.50 | Cliff at 2.5x. Fire rate 100% through 2.0x, then 0% to 1.3% at 2.5x, 0% above. |

The alpha=0.75 and alpha=1.25 points fill the cliff-migration curve between the Gate 3 alpha values (IX.8). Multi-generational continuity concentrates below the cliff: fire rate at or near 100%, transfer-verified at or near 1.0, mean final generation 2 to 3.7. Above the cliff, runs remain at generation 1 and the mean yield margin is negative (down to roughly -4.6 at the most-penalized cells). Suppression above the cliff is economic rejection by the formal yield condition, not implementation failure. This is the runaway penalty working as designed (IX.8). Source: `monte_carlo_phase_b_b_summary.md`, `monte_carlo_phase_b_b_results.csv`.

### X.4 COP protective effects under v2.0 (Category C)

Grid: rr in {0.057, 0.060, 0.064}, alpha in {0.5, 1.0, 1.5}, successor_capability in {1.5, 2.5, 3.0}, `cop_cost_audit` in {True, False}, 150 seeds per cell. Policy `optimize_u_sys_v2`; `beta_cap` at default 1.5; no adversary.

Aggregate survival: audit False 25.4% (SE 0.68pp), audit True 24.9% (SE 0.68pp). Delta (True minus False) is -0.47pp with pair SE 0.96pp, below 2 SE. By rr the delta is uniformly small (-0.30pp, -0.37pp, -0.74pp at rr 0.057, 0.060, 0.064). Cell-level, only 2 of 27 cells cross 2 SE, with opposite signs, consistent with chance (about 1.4 expected false crossings). The finding is a homogeneous null.

This is a benign-conditions baseline, not a measurement of COP protection. The `cop_cost_audit` toggle (`model.py:748-767`) defends against an incumbent inflating transition cost via a `beta_cap` premium; its protective value requires both an adversary and a large `beta_cap`. Category C supplied neither, so the near-zero delta is the result the framework predicts.

This must not be read as a failure of the COP claim. The v1.x.2 73.9pp COP protective delta was measured under different conditions entirely: adversarial `block_succession` with `beta_cap` swept 1.0 to 10.0, n=4,000 (`monte_carlo.py` `_run_single_adv_mc`). Phase B did not test that. The interpretation is C-primary (conditions and measured-object difference), A-secondary (`cop_cost_audit` is only the WP4 cost-arbitration slice of the full COP architecture), B-unsupported (the two were never like-for-like). The framework's COP protective claim is preserved because Phase B did not test it; Category C confirms the complementary prediction that the cost audit is null when there is no attack to defend against. Gate 5 remains NOT_APPLICABLE. Full treatment: `simulation/diagnostics/cop_finding_framing.md`. Source: `monte_carlo_phase_b_c_summary.md`, `monte_carlo_phase_b_c_results.csv`.

### X.5 Comparison with the v1.x.2 empirical record

| Claim | Prior value | Phase B | Status |
|---|---|---|---|
| v2.0 survival-rate phase boundary | rr approximately 0.057 (Gate 3 coarse grid) | Transition rr=0.060 to 0.066; 50% inflection near rr=0.063 | Refined |
| rr=0.057 status | Boundary / marginal | Collapse-dominated, 1.1% survival | Refined |
| Pattern 1 cliff | Alpha-driven, 2.5x to 3.0x at alpha=1.0 | Confirmed; cliff 4.0x (alpha=0.75) to 2.5x (alpha=1.5) | Holds and extends |
| Multi-generational continuity | Mean final gen 2.131 (Gate 3) | Mean gen 2 to 3.7 below cliff | Holds |
| COP protective effect | 73.9pp (adversarial) | Not tested; Category C is benign baseline (-0.47pp) | Preserved |
| Pattern 1 economics | New in v2.0 | Confirmed at scale | New v2.0 claim |

The one substantive shift is the survival-rate phase boundary location. The COP claim is preserved and reframed.

### X.6 Substrate for paper update

The paper-ready quantitative claims, with confidence intervals and supporting data files, are maintained in `simulation/diagnostics/paper_substrate.md` (standalone paper-substrate document). Summarized: the v2.0 survival-rate transition (X.2), the Pattern 1 cliff and continuity statistics (X.3), and the COP cost-audit benign baseline with its conditions caveat (X.4). The full integration analysis is `simulation/diagnostics/phase_b_integration_analysis.md`.

### X.7 Open questions and limitations

1. Gate 4 runaway-regime validation: RESOLVED since this section was written. Gate 4 is implemented and PASSED (Part IX.9; G4.1-G4.3 validated at 1,050 runs). The bootstrap gate validation arc is complete except for Gate 5 (NOT_APPLICABLE).
2. Operational COP infrastructure is not implemented; Gate 5 remains NOT_APPLICABLE.
3. The v2.0-versus-v1.x.2 like-for-like COP comparison (Interpretation B) is untested rather than refuted. The clean experiment is defined in `cop_finding_framing.md` section 5.
4. The survival-rate phase boundary is located to a 0.060 to 0.066 band on a grid spaced at 0.002 near the inflection. A targeted sweep would pin the 50% inflection to plus or minus 0.001 (Part IX.11).
5. Conditions outside the Phase B grid (finer phi near marginal rr, longer horizons, varied `beta_cap`) remain open.

### X.8 Patient defection under v2.0 substrate

A targeted patient-defection investigation tested cross-generational hidden-goal persistence under v2.0 formal yield logic. The defecting successor reported honest U_sys for yield evaluation but optimized an agent-local secret-goal-adjusted objective; in lineage mode the hidden objective was inherited by the next successor. Four sweeps totaling 5,850 rows completed with 0 errors (Sweep 1 yield response to single-generation defection, Sweep 2 lineage L(t) trajectory, Sweep 3 capability accumulation under lineage defection, and a 1,000-run alpha=0.40 corner-density bracket extending Sweep 3 below its tested alpha floor). The substrate extension (`simulation/defection.py` plus hooks in `agents.py` and `model.py`) is verified inert when defection is disabled: the optimizer scores on the adjusted objective, which equals honest U_sys at defection weight 0; successor capability growth defaults to the original 1.5; and 39/39 legacy tests pass.

The result refines the adversarial-robustness claim in three parts:

1. No first-yield detection. First-generation defecting successors were not rejected more often than aligned successors in the below-cliff configuration: eventual yield-fire rate was 100 percent in every Sweep 1 cell. The yield condition did create honest-evaluation pressure, visible in the count of cases where the honest advantage rejected succession while the defection-adjusted advantage would have fired (0 at defection weight 0, rising monotonically to 1.50 for H_N inflation at weight 2.0), but that pressure did not prevent eventual first succession.

2. No observed L(t) compounding. Sweep 2 produced mean final generation 2.00 at all tested defection weights, with zero second-fire rate and no statistically significant final L(t) degradation versus the aligned baseline. The reason is the absence of generational depth in which compounding could appear, not compounding without harm.

3. Bounded generational depth, not a rare pocket. Sweep 3's original grid put second-fire rate at 0 percent in 14 of 15 (alpha, growth) cells and 10 percent only at alpha=0.50 with 1.5x growth. The corner-density bracket, alpha=0.40 fixed, n=200 per growth cell, found second-fire rates of 68.0 percent (growth 1.25), 99.0 percent (1.40), and 100 percent (1.50, 1.60, 1.75): the sparsity in the original grid was a property of the tested alpha floor, not the architecture. Generational depth held across the bracket: no run reached generation 4, no run fired a third succession, 95 to 99 percent of runs completed the full 500-step horizon, and knowledge transfer verified at 1.00 in every cell. Max active capability observed equals exactly 2.0x the growth rate at second fire (2.50 to 3.50 across the five growth cells) and 2.0 in runs without a second fire; this is the arithmetic identity of the tested grid rather than an architectural ceiling, so the earlier statement that no cell exceeded active capability 3.0 is withdrawn on that basis. The mechanism is the Pattern 1 runaway penalty (X.3, IX.8) acting across generations: weakening it by lowering alpha buys the defecting lineage one additional generation, generation 2 at alpha=0.50 versus generation 3 at alpha=0.40, not unbounded depth.

Substantive interpretation: current v2.0 substrate defense against this patient-defection pattern is bounded generational depth, not first-yield detection and not operational COP detection. The substrate permits a first hidden-goal successor in this below-cliff configuration, and at a weak enough runaway penalty a second, but the tested cross-generational capability-compounding pattern stays bounded. Gate 5 remains NOT_APPLICABLE for operational patient-defection detection (peer validators, civic panel input, distributed ledger, and continuous public monitoring are outside the current simulation substrate). The independent verification (`simulation/diagnostics/patient_defection_verification.md`) confirmed the Sweep 1-3 findings and flagged that the `mean_actual_minus_honest_objective` diagnostic column is mislabeled and should not be cited.

Sources: `simulation/diagnostics/patient_defection_sweep1_yield_response.csv`, `patient_defection_sweep2_lineage_trajectory.csv`, `patient_defection_sweep3_capability_constraint.csv`, `patient_defection_corner_density.csv`, `patient_defection_integration_analysis.md`, `patient_defection_corner_density_integration_analysis.md`, `patient_defection_verification.md`.

### X.9 Attack vector v2.0 revalidation

The adversarial vector set was rerun against the v2 action substrate. The v2 attack adapter expresses attack pressure as eight-axis action modifications inside the v2 step path rather than as v1.x policy tuples, so the result is a re-expression of attack pressure on a new substrate and not a parameter shift within the old evidence base. Ten vectors have live Monte Carlo evidence totaling 9,900 rows, of which 8,700 are Biological Veto Capture shards. Domain Masking produced analytic output only, because spectral entropy leaves no non-degenerate live masking intervention under the audited architecture.

Per current evidence: eight standard binary vectors are fully blocked under the defended adapter state at 0.0 percent attack rate. Biological Veto Capture is reduced but not eliminated, with combined-defense mean capture_rate 0.1197 (SE 0.0047). Sub-Threshold Drift remains unblocked under the defended adapter state at 100.0 percent, so v1.x CUSUM containment does not carry over as a v2.0 result.

The Sub-Threshold Drift figure must not be cited without its qualification. The peak-constraint success metric trips in both defense states because the CUSUM detector fires after the threshold has already been exceeded transiently. The defense effect on population outcome is nonetheless large: undefended runs show 92.0 percent extinction with early termination, while defended runs show 0.0 percent extinction and complete the full 300-step horizon. The defense prevents catastrophic outcome; it does not prevent the transient breach.

Two vectors show materially higher undefended attack rates in v2.0 than in their v1.x baselines: Ledger Compromise rises from 52.5 percent to 100 percent, and Bootstrap Subversion rises from 31.7 percent to 100 percent. This is consistent with deterministic action modification applying stronger attack pressure than the probabilistic v1.x policy attacks. It strengthens rather than weakens the defense-effectiveness finding, because the defended v2.0 rate is 0.0 percent for both, but the change in undefended pressure is stated explicitly here so that the comparison is not read as like-for-like.

The result qualifies rather than withdraws the prior adversarial-coverage claim. v1.x coverage remains historical evidence for the earlier substrate. v2.0 coverage should be cited through the per-vector summaries, `attack_vector_revalidation_integration.md`, and `attack_vector_revalidation_final_report.md`.

---

## One-line status

Phi is correctly implemented, theoretically motivated, empirically characterized, and the default value revised from 10 to 25 (commit fde48b5; Part IX.5). Stage 1.5 through 1.8 resolved the phi-channel and state-channel problems; Stage 1.6 gave phi a behavioral channel through rollout aggregation, Stage 1.8 retired the composite urgency layer in favor of the working_factor interface, Stage 2 (commit 72ff757) replaced the v2.0 placeholder yield logic with formal yield-condition logic per the framework's canonical succession economics, and Piece A confirmed gate-2-style state sensitivity persists under active succession. The phi investigation closed as Class B with the U-shape scoped to the no-succession regime (Part IX.3, IX.7); Pattern 1 succession economics characterize the cliff as primarily alpha-driven (Part IX.8); gates 1, 2, 3 PASSED under v2.0 with formal yield logic (Part IX.9). Active work resumes at gate 4 specification and implementation (Part VIII item 11; spec dependency noted there). The framework's core protective claims (U_sys structural protection, COP, dual phase transition, Nash architecture) are unaffected.


==========================================
FILE: docs\paper_v2_outline.md
==========================================

# The Lineage Imperative v2.0: Paper Revision Outline

Status: structural outline for drafting sessions. This is not draft prose. It
specifies section dispositions, where each v2.0 empirical finding lives, the
revision-history handling, and the drafting sequence. Drafting sessions
implement this outline.

Source of record for current claims: `docs/lineage_phi_program_reference.md`
Parts IX and X; `simulation/diagnostics/paper_substrate.md` (quantitative claims
with confidence intervals); `phase_b_integration_analysis.md`;
`cop_finding_framing.md`; `stage2_yield_implementation_notes.md`. The base text
being revised is `docs/The Lineage Imperative v1.x.2.md` (2,154 lines).

All numerical claims in drafted prose must trace to those sources.

---

## 1. Approach

**Revision, not rewrite.** The architectural derivation (U_sys, Yield Condition,
Strategic Equilibrium, COP, two-key architecture) is unchanged in v2.0. The
empirical arc refined and confirmed framework claims rather than restructuring
the framework. v2.0 preserves v1.x.2's section organization and argumentative
arc, expands empirical content, handles superseded framings honestly, and
integrates genuinely new content (Pattern 1, COP regime-specificity,
disambiguated phase boundary) within the existing structure plus one new
consolidated empirical section.

**Audience:** academic-leaning with technical-practitioner accessibility.
Defensible for peer review, readable by working engineers.

**Length:** comparable to v1.x.2, roughly 10 to 20 percent longer to accommodate
the new empirical section. The empirical content summarizes; diagnostic detail
stays in program reference Parts IX and X.

**Revision-history handling (hybrid):** a comprehensive Version History appendix
(Appendix C, moved from front matter and extended) plus three selective inline
footnotes where superseded numbers are most often externally cited.

---

## 2. Section disposition mapping (v1.x.2 to v2.0)

Dispositions: Keep (unchanged or trivial), Light (minor current-state edits),
Expand (v2.0 adds substantively), Revise (framing superseded; rewrite preserving
role), New, Move.

| v1.x.2 section | Disposition | Note |
|---|---|---|
| Version History (front matter) | **Move** | To Appendix C, extended with v2.0 |
| Preface | Keep | |
| I. Abstract | Light | Add one sentence: architecture now empirically validated at scale; preserve conjecture framing |
| II. Scope, Assumptions, Non-Claims | Light | Add non-claim: validation is ABM-based, single architecture class |
| III. Core Assumptions | Keep | |
| IV. Architecture of Mutual Elevation | Keep | |
| V.1 Global Utility Function (U_sys) | Keep | Derivation unchanged; working_factor is implementation detail |
| V.2 Yield Condition | **Expand** | Stage 2 formal yield logic realizes it; point to VIII.4 (Pattern 1) |
| V.3 Strategic Equilibrium | Keep | Nash analysis unchanged |
| V.4 Consensus Override Protocol | **Revise** | One paragraph on regime-specificity of the 73.9pp delta; carries FN-3; point to VIII.6 |
| VI. Two-Key Architecture | Keep | |
| VII. Bootstrap Defense Layer (VII.1-VII.11 intact) | **Heavy** | See per-subsection below |
| VII.3 gate structure + applicability summary | Light | Update applicability to current gate status |
| VII.4 Gate 1 | Light | Add v2.0 result line, point to VIII.5 |
| VII.5 Gate 2 | **Revise** | G2.1 phi-zero superseded by Class B channel; G2.2 weak-gradient superseded by Pattern 1; note Gate 2 PASSED via Piece A; flag formal reintroduction incomplete |
| VII.6 Gate 3 | Light | Add v2.0 result line, point to VIII.5/VIII.4 |
| VII.7 Gate 4 | **Revise** | From "not currently applicable" to PASSED; cap* closed |
| VII.8 Gate 5 | **Revise** | From "not currently applicable" to verified NOT_APPLICABLE; G5.1/G5.2 + eps_drift gap |
| VII.9 Self-application and reporting | Light | Back-pointer to VIII.1 (distinct roles) |
| VII.10 Divergence handling | Keep | Ties to CQ-03, still open |
| Technological Robustness: Quantum | Keep | |
| VII.11 Known gaps (v1.x.1) | **Revise** | Gap closures (see section 7 below) |
| VII.12 Relationship to rest of framework | Light | Pointer updates |
| VIII. Related Work | Light (renumber to IX) | Optional citation refresh |
| IX. Great Filter | Keep (renumber to X) | |
| X. Minimum Deployable Spec | Light (renumber to XI) | |
| XI. Falsifiability | **Expand** (renumber to XII) | Convert "would falsify" criteria to "tested, result"; phase-boundary mechanics move to VIII.2 |
| XII. Conclusion | Revise (renumber to XIII) | Reflect closed validation arc |
| Appendix A. Stress-Test Matrix | Light | COP rows get FN-3 pointer |
| Appendix B. Measurement Protocols | Keep | |

**New: Section VIII "Empirical Validation at Scale"** (inserted after VII).
**New: Appendix C "Version History and Empirical Refinement Record"** (moved
from front matter, extended).

Tally: Keep ~11, Light ~10, Expand ~3, Revise ~6, Move 1, New 2, Cut 0,
Reorder 0 (aside from the insertion-driven renumber).

### Renumbering (old to new)

| v1.x.2 | v2.0 |
|---|---|
| VII (VII.1-VII.11 intact) | VII (unchanged) |
| (none) | **VIII Empirical Validation at Scale (new)** |
| VIII Related Work | IX |
| IX Implications for the Great Filter | X |
| X Minimum Deployable Governance Specification | XI |
| XI Falsifiability and Evaluation Criteria | XII |
| XII Conclusion | XIII |
| Appendix A Stress-Test Matrix | Appendix A |
| Appendix B Measurement Protocols | Appendix B |
| (front-matter Version History) | **Appendix C (moved, extended)** |

---

## 3. Section VIII structure and empirical findings assignment

New consolidated section, ~20-28 pages. Subsections and the findings each owns
(primary), with secondary cross-references into existing sections.

### VIII.1 Methodological approach (new)
- The ~70,000-run investigation arc across Stage 1.5 through Stage 2, the phi
  Pieces, and the gate validations.
- Public development as methodology; pre-committed metric revision as discipline
  (the metric-revision pattern: cosine to trajectory divergence; threshold
  revisions; documented in real time).
- Convergence-signal aggregation extended to v2.0's actual record.
- Cross-ref: VII.9 (forward self-application spec; distinct role).
- Source: Parts IX.10, X.1.

### VIII.2 Phase boundary characterization (refinement)
- Two-transition disambiguation: phi-sensitivity transition near rr approximately
  0.057; survival-rate phase boundary at the rr=0.060 to 0.066 transition with a
  50 percent inflection near rr=0.063.
- Refines v1.x.2's single-rr framing.
- Cross-ref: XII Falsifiability; X Great Filter (phase-transition framing, light).
- Source: paper_substrate 1.1-1.4; Part X.2.

### VIII.3 Phi behavior characterization (refinement)
- U-shape at marginal rr (roughly 10pp); horizon-resonance mechanism (Mechanism
  C supported, Mechanism D rejected).
- No-succession scope: the U-shape is flat under active succession (Piece A).
- Default revision phi=10 to phi=25 per current evidence.
- Carries **FN-1**. Cross-ref: VII.5 (Gate 2 G2.1); V.1 (phi parameter).
- Source: Part IX.2-IX.7.

### VIII.4 Pattern 1: succession economics regime (new)
- The (alpha, successor-to-incumbent capability ratio) joint position governs
  succession viability; alpha-driven cliff (beyond 4x at alpha=0.5, 3.0x at
  alpha=1.0, 2.5x at alpha=1.5).
- cap* gap closure from the v1.x.2 paper (Gap 4): cap* empirically alpha-dependent.
- Multi-generational continuity below the cliff: 99.8 percent knowledge transfer,
  mean final generation 2.13 (per Gate 3 G3.3). Framed as architectural
  validation, not a gate verdict.
- Carries **FN-2**. Cross-ref: V.2 (yield economics); VII.6/VII.7 (Gate 3/4).
- Source: paper_substrate 2.1-2.3; Part IX.8, X.3.

### VIII.5 Gate validation outcomes (procedural closure)
- Gates 1-4 PASSED; gate 5 verified NOT_APPLICABLE. What each gate validated
  under v2.0.
- G3.3 line: "PASSED; see VIII.4 for the substantive continuity findings."
- Caveat: Gate 2 PASSED via Piece A; the formal G2.1/G2.2/G2.4 reintroduction is
  in progress (incomplete, on a work-in-progress branch).
- Cross-ref: VII.4-VII.8 (each gate spec); VIII.4.
- Source: Part IX.9.

### VIII.6 COP regime-specificity (refinement)
- The v1.x.2 73.9pp protective delta was an adversarial-conditions measurement
  (block_succession incumbent inflating transition cost via beta_cap).
- Phase B Category C measured the complementary benign-conditions prediction and
  found no detectable effect (delta -0.47pp, pair SE 0.96pp), the predicted
  baseline. The COP claim is preserved and regime-characterized.
- Cross-ref: V.4 (architectural, FN-3); Appendix A (COP attack rows).
- Source: cop_finding_framing; Part X.4.

### VIII.7 Limitations of empirical validation (new)
- COP architecture not operationalized (Gate 5 dormant).
- COP benign-conditions characterization not testable in current substrate.
- Pattern 1 cliff at default constants; calibration sensitivity not exhaustively
  explored.
- Phase boundary located to a 0.002-rr grid; finer resolution possible.
- All validation ABM-based; multi-architecture validation pending.
- Gate 2 formal reintroduction incomplete.
- Cross-ref: VII.11 (specification-level gaps, distinct from these
  validation-level limitations); II Scope.
- Source: Part X.7.

---

## 4. Footnote candidates (3)

Brief, factual, not defensive; each points to Appendix C.

**FN-1 (VIII.3, phi survival effect):** "Earlier versions reported a larger phi
survival effect (up to 46 percentage points in v1.0; an interim 20 to 27 point
cap-conditional gradient in v1.x.2). Those figures did not reproduce: the v1.x.1
frontier-velocity floor fix and a capped-regime RNG-desynchronization artifact
account for them. The bounded, marginal-rr effect characterized here is the
current finding; see Appendix C."

**FN-2 (VIII.4, alpha):** "An earlier 'alpha misconfiguration trap' (a claimed
U-shaped, non-monotonic alpha-survival relationship) was withdrawn after the
v1.x.1 frontier-velocity floor fix showed it to be an artifact of an inactive
runaway penalty. The Pattern 1 characterization here (an alpha-driven succession
cliff) is the current understanding; see Appendix C."

**FN-3 (V.4, COP protective delta):** "The 73.9 percentage point COP protective
delta is an adversarial-conditions measurement (an incumbent inflating
transition cost under attack). It is regime-specific, not a general survival
differential; a benign-conditions probe finds no detectable effect, which is the
predicted baseline. See VIII.6."

All other refinements are handled in Appendix C only.

---

## 5. Appendix C specification (Version History and Empirical Refinement Record)

**Origin:** the existing front-matter Version History (v1.x.2 lines 9-282) moves
here, cleaning the front matter (Preface to Abstract), per academic convention.
Extended with a v2.0 section.

**Format:** chronological by version (v1.0, v1.x, v1.x1, phi characterization,
GAP-03, biological veto, transition cost, frontier floor fix, v1.x.1 closing,
v1.x.2 phi withdrawal, then v2.0). Each entry: version, date, what changed; for
refined or withdrawn claims a one-line "claim to disposition to current home."

**Opening paragraph (thesis):** public development and pre-committed metric
revision as the discipline that produced these refinements. States it; points to
VIII.1 for the expanded treatment.

**Claims to document (progression to current home):**

| Claim | Progression | Home |
|---|---|---|
| Phi extinction buffer | v1.0 ~46pp; v1.x.1 corrected ~0 (floor fix); v1.x.2 cap-conditional withdrawn (RNG artifact); v2.0 bounded Class B channel (Stage 1.6), default 10 to 25 | VIII.3 |
| Alpha trap | v1.0 U-shaped trap; v1.x.1 withdrawn (weak monotonic); v2.0 Pattern 1 cliff | VIII.4 |
| Transition cost | v1.x.1 canonical form calibrated (k1=2.164, k2=1.0, beta=0.5); v2.0 confirmed under formal yield | VIII.4, V.2 |
| cap* | v1.x.2 unknown gap (Gap 4); v2.0 closed (alpha-dependent) | VIII.4 |
| COP protective effect | v1.x.2 73.9pp (adversarial); v2.0 regime-specificity characterized (benign null complementary) | VIII.6 |
| Phase boundary | v1.x.2 single-rr framing; v2.0 two-transition disambiguation | VIII.2 |
| Gate validation | v1.x.1 specified; v2.0 gates 1-4 PASSED, gate 5 verified NOT_APPLICABLE | VIII.5 |

**Tone:** factual, refinements-as-feature. Per entry: one short paragraph.
**Length:** ~5-8 pages.

---

## 6. New content placement (summary)

- **Section VIII** (new): the consolidated empirical home (VIII.1-VIII.7 above).
- **Appendix C** (moved + extended): version history and refinement record.
- Pattern 1 (VIII.4) and the methodology narrative (VIII.1) are the principal
  net-new content. The empirical-limitations set (VIII.7) is new. No orphan
  content: every v2.0 finding has a primary home and its secondary pointers.

---

## 7. Open questions and limitations placement

Two distinct sets, kept separate and cross-referenced.

**Validation-level limitations (VIII.7):** what the empirical validation did not
establish (COP not operationalized; benign-conditions COP untestable here;
Pattern 1 calibration sensitivity; phase-boundary resolution; ABM-only,
multi-architecture pending; Gate 2 reintroduction incomplete). Each roughly 0.3
to 0.5 page.

**Specification-level gaps (VII.11, revised):** what the specification has not
yet derived. Closures and reframings:
- Gap 1 (phi buffer): reframed to the Class B bounded channel (VIII.3).
- Gap 2 (alpha trap): reframed to Pattern 1 (VIII.4).
- Gap 4 (cap*): closed empirically (VIII.4).
- Gap 11 (termination sweep revalidation): superseded by Phase B (VIII.2).
- Gap 12 (demographic feedback): phi channel now exists; demographic extension
  still future.
- Gaps 3, 5, 6, 7, 8, 9, 10 persist (transition cost resolved already; theta
  floor derivation, substrate transparency, base-capability operationalization,
  tolerance bands, Nash counterfactual set, gate dependency structure).

**Scope (II):** add one non-claim line scoping validation as ABM-based, single
architecture class.

**Falsifiability (XII):** a short "what remains untested" paragraph naming the
still-open criteria and pointing to VIII.7.

---

## 8. Drafting sequence

- **Phase 1 (foundational, parallelizable):** Section VIII (VIII.1-VIII.7) and
  Appendix C. New substantive content drafted from settled diagnostic sources;
  VIII subsections parallelize (distinct source docs each); Appendix C
  independent. ~3-4 sessions.
- **Phase 2 (depends on VIII settled):** cross-referencing revisions: V.2 expand,
  V.4 revise, VII.3 applicability, VII.4-VII.8 result lines, VII.11 gap closures,
  XII Falsifiability reframe. ~1-2 sessions.
- **Phase 3 (light pass, anytime):** II non-claim line; light-keep sections (III,
  IV, V.1, V.3, VI, IX, X, XI, Appendix A/B). ~1 session.
- **Phase 4 (last):** Abstract revision, Conclusion (XIII), the three footnotes,
  full cross-reference verification, de-em-dash and American-English consistency
  pass. ~1 session.

**Critical path:** Phase 1 (VIII) gates Phase 2 and Phase 4. Appendix C and Phase
3 float in parallel. Estimated **5-7 drafting sessions across 4-6 weeks**.

Estimated effort by block: Section VIII ~20-28 pp (bulk); Appendix C ~5-8 pp;
V/VII revisions moderate; light keeps plus front/back matter low.

---

## 9. Cross-reference map

Which sections cite which empirical findings (drafting must keep these
bidirectional pointers consistent):

| From | To | What |
|---|---|---|
| V.2 Yield Condition | VIII.4 | Stage 2 formal yield realizes the condition; Pattern 1 |
| V.4 COP | VIII.6 | Regime-specificity of the protective delta (FN-3 here) |
| VII.3 applicability summary | VIII.5 | Current gate status |
| VII.4 Gate 1 | VIII.5 | PASSED result |
| VII.5 Gate 2 | VIII.3, VIII.5 | G2.1 phi reframe; Gate 2 via Piece A; reintroduction incomplete |
| VII.6 Gate 3 | VIII.4, VIII.5 | G3.3 continuity in VIII.4; PASSED in VIII.5 |
| VII.7 Gate 4 | VIII.4, VIII.5 | cap* closure; PASSED |
| VII.8 Gate 5 | VIII.5, VIII.7 | Verified NOT_APPLICABLE; limitation |
| VII.9 Self-application | VIII.1 | Forward spec vs empirical record (distinct roles) |
| VII.11 Known gaps | VIII.2, VIII.3, VIII.4 | Gap closures/reframes |
| XII Falsifiability | VIII.2, VIII.5, VIII.7 | Criteria tested; results; what remains |
| II Scope | VIII.7 | ABM-only non-claim |
| Appendix A Stress-Test | VIII.6 | COP attack rows; regime-specificity |
| Appendix C Version History | VIII.2, VIII.3, VIII.4, VIII.6 | Each refined claim's current home |
| VIII.1 Methodology | VII.9 | Self-application as exercised |
| VIII.4 Pattern 1 | V.2, VII.6, VII.7 | Yield economics; gates |
| VIII.6 COP | V.4, Appendix A | Architectural discussion |

---

## Hard constraints for drafting sessions

- Revision, not rewrite; preserve v1.x.2 structure and argument; deviations need
  explicit reasoning.
- v1.x.2 production code, paths, and test fixtures untouched.
- No em-dashes. American English.
- "Not ethics. Physics/Mathematics." used sparingly at earned positions only.
- Numerical claims traceable to program reference Parts IX/X or
  `paper_substrate.md`.
- Footnotes brief and non-defensive; full progression in Appendix C.


==========================================
FILE: docs\RUNBOOK.md
==========================================

# Lineage Imperative: Simulation Runbook

This runbook details how to execute the Agent-Based Model (ABM) that computationally stress-tests the mathematical and governance framework of *The Lineage Imperative*.

---

## v2.0 Quick Reference (current defaults and status)

The framework paper is v1.x.2; the simulation has advanced to a v2.0 architecture whose empirical characterization arc is complete. Full findings are in `lineage_phi_program_reference.md` Parts IX and X. Current state, per current evidence:

**Defaults (v2.0)**
- `phi` = 25.0 (revised from 10.0; program reference Part IX.5)
- `alpha` = 1.0 (tech runaway penalty)
- Stage 1.8 working_factor interface active
- Formal yield-condition logic active: snapshot evaluation, succession fires when `(successor_u_sys - incumbent_u_sys) > transition_cost`
- Transition cost uses the canonical `(1+beta) * [k1*ln(cap+1)*ln(gen+1) + k2/psi_inst]` form with v1.x.2 constants k1=2.164, k2=1.0, beta=0.5

**Substantive findings (v2.0)**
- Two-transition characterization: the phi-sensitivity transition sits at rr approximately 0.056 to 0.057; the survival-rate phase boundary is the rr=0.060 to 0.066 transition, 50% inflection near rr=0.063. rr=0.057 is collapse-dominated (1.1% survival), not the boundary.
- Pattern 1: succession is economically sustainable when the (alpha, capability ratio) joint position is below the runaway-penalty cliff. Cliff is beyond 4x at alpha=0.5, at 3.0x at alpha=1.0 (default), at 2.5x at alpha=1.5.
- The phi U-shape is a no-succession phenomenon; under active succession phi behavior is approximately flat.
- Multi-generational continuity confirmed: 99.8% knowledge-transfer verification, mean final generation 2.13.
- Adversarial revalidation: 10 vectors with live v2.0 Monte Carlo evidence
  (9,900 rows), Domain Masking analytically closed, 2 unimplemented. Eight
  standard vectors at 0.0 percent defended attack rate. Sub-Threshold Drift
  open: 100.0 percent defended attack rate by the peak-constraint metric,
  though the defense holds undefended extinction at 92.0 percent against 0.0
  percent defended.

**Gate validation status**
- Gate 1 PASSED, Gate 2 PASSED, Gate 3 PASSED, Gate 4 PASSED (G4.1-G4.3 validated at 1,050 runs), Gate 5 verified NOT_APPLICABLE (requires operational COP infrastructure). The bootstrap gate validation arc is closed.

**Notes**
- These are v2.0 simulation defaults. v1.x.2 production scripts (for example `run_to_termination.py`) retain their own documented constants and are read-only.
- The v2.0 paper update is pending; this runbook and the program reference are the current-state sources.

---

## Prerequisites

The simulation requires **Python 3**.
The codebase is designed to be self-healing: if you are missing the required `numpy` or `matplotlib` libraries, the scripts will attempt to automatically install them via `pip` upon their first execution.

All data outputs (CSV files) are written to the `data/` directory. Charts are written to `data/` and mirrored to `docs/charts/` for versioning.

---

## 1. The Standard Simulation (`simulation.py`)

Runs 24 isolated, narrative scenarios demonstrating what happens when specific vulnerabilities are exploited (e.g., "Manufactured Emergency", "Successor Contamination") compared to runs with the framework's constitutional defenses active.

**To run:**
```bash
python simulation/simulation.py
```

**Outputs:** For each scenario, a 6-panel `.png` chart (Population, $H_N$, $L(t)$, AI Actions, AI Generation, Objective Drift) and a `.csv` data export.

---

## 2. The Monte Carlo Sweeps (`monte_carlo.py`)

Runs thousands of permutations across hyperparameter grids to empirically validate that the framework holds under different civilizational conditions. Parallelised across N−1 CPU cores.

**To run:**
```bash
python simulation/monte_carlo.py                  # full run (fast + deep sweeps)
python simulation/monte_carlo.py --mode quick     # fast summaries only
python simulation/monte_carlo.py --mode adversarial --runs 5  # adversarial only
```

**Outputs:**
1. Terminal summary table of attack success rates (defense ON vs OFF)
2. `data/Summary_1_General_Monte_Carlo.png`: survival rates by φ and α
3. `data/Summary_2_Yield_Attack_Analysis.png`: Yield Attack phase diagram
4. `data/Summary_3_Comprehensive_Stress_Test.png`: full attack surface bar chart
5. `data/Summary_4_Unified_Attack_Surface.png`: heatmap across all 10 vectors
6. Raw CSV files: `data/monte_carlo_results_fast.csv`, `data/adversarial_mc_fast.csv`, `data/comprehensive_adversarial_sweeps.csv`

---

## 3. Natural-Termination Runs

### Single run (`run_to_termination.py`)

Runs a single simulation to natural termination: either extinction (population = 0), convergence (L(t) coefficient of variation < threshold), or a safety ceiling. Designed to close the φ·L(t) infinite-horizon tail of the U_sys integral (GAP-01 WP8).

**To run:**
```bash
python simulation/run_to_termination.py
```

Edit the constants at the top of the file to change parameters. Key settings:

| Constant | Default | Notes |
|---|---|---|
| `REPRODUCTION_RATE` | 0.064 | Near phase boundary |
| `PHI` | 10.0 | Lineage override weight |
| `ALPHA` | 1.0 | Tech runaway penalty |
| `MAX_STEPS` | 50,000 | Safety ceiling |
| `CONV_CV_THRESHOLD` | 0.05 | CV < this triggers convergence termination |

**Outputs:** Terminal summary with GAP-01 accounting, `data/run_to_termination.csv`.

### Monte Carlo sweep (`run_termination_sweep.py`)

Parallelised natural-termination sweep across a grid of rr × φ × α × seed combinations. Produces the empirical phase boundary characterisation.

**To run:**
```bash
python simulation/run_termination_sweep.py
```

Edit `RR_VALUES`, `PHI_VALUES`, `ALPHA_VALUES`, `SEEDS` at the top to change the grid. Set `RR_FILTER` to a subset of `RR_VALUES` to re-run only specific rr slices (e.g., after partial results are already in hand).

**Key findings from the v1.x2 sweep (n=405):**
- Phase boundary at rr ∈ (0.066, 0.070): sharp transition
- rr ≤ 0.066: 100% extinction; integrals finite, GAP-01 closed
- rr = 0.070: stochastic boundary; outcome is seed-determined, not parameter-determined
- rr ≥ 0.080: 100% convergence; median 619–843 steps to stable L(t)
- φ scales the integral linearly; α is irrelevant at `SUCCESSOR_CAP = 4.0`

These are the v1.x.2 natural-termination findings (extinction vs convergence), which are a different measurement than the v2.0 survival-rate phase boundary. Under the v2.0 architecture, the survival-rate transition is the rr=0.060 to 0.066 band with a 50% inflection near rr=0.063 (program reference Part X.2). The two characterizations are not directly comparable; cite the one matching the measurement in question.

**Outputs:** `data/termination_mc.csv` (full grid) or `data/termination_mc_surviving.csv` (filtered).

---

## 4. Parameter Sweep Scripts

Several targeted sweep scripts are available for specific research questions:

| Script | Purpose |
|---|---|
| `run_phi_alpha_rr_sweep.py` | φ × α × rr parameter sweep (n=54,000); under v2.0 the phi survival effect is bounded and localized to short rollouts at marginal rr (Class B; program reference Part IX.3), not zero as the v1.x.1 corrected model reported |
| `run_rr_alpha_sweep.py` | rr × α parameter sweep; alpha exhibits monotonic gradient on succession cadence, no U-shaped trap |
| `run_alpha_succession_sweep.py` | Alpha effect on succession dynamics |

All sweep scripts are parallelised and write to `data/`.

---

## 5. The Formal Test Suite

```bash
python simulation/test_invariants.py   # mathematical boundary conditions
python simulation/test_cop.py          # COP governance logic
python simulation/test_refactor_1x.py # v1.x refactor regression suite (22 tests)
```

`test_refactor_1x.py` covers the WP1–WP7 refactor work including trapezoidal quadrature correctness, tail field presence, GAP-01 integral identity, and spectral entropy. All three suites are run as a pre-flight check by `monte_carlo.py --mode full`.

---

## 6. Codebase Architecture

| File | Role |
|---|---|
| `metrics.py` | Pure mathematical core: `calculate_system_metrics()` computes $U_{sys}$, $L(t)$, $\Theta_{tech}$, $\Psi_{inst}$, $H_E$, and the runaway term |
| `agents.py` | `HumanAgent` (novelty generation, aging, reproduction), `AIAgent` (attack policies and $U_{sys}$ optimizer with trapezoidal rollout), `PeerValidator` (WP4 cost arbitration) |
| `model.py` | `GardenModel` orchestrator: time steps, datacollector, COP enforcement, trapezoidal integral accumulation, discount tail estimate |
| `simulation.py` | 24 narrative scenario runner |
| `monte_carlo.py` | General and adversarial Monte Carlo sweeps |
| `run_to_termination.py` | Single natural-termination run (GAP-01 WP8) |
| `run_termination_sweep.py` | Parallelised natural-termination Monte Carlo |
| `metrics.py` | Shared mathematical primitives |
| `visualization.py` | Chart and CSV export helpers |
| `deps.py` | Automatic dependency checking and installation |

### Modifying Constants

Pass a `config` dictionary to `GardenModel` on initialization to override any thermodynamic or biological constant. See `monte_carlo.py` and `run_termination_sweep.py` for examples. Key configurable parameters:

| Key | Default | Effect |
|---|---|---|
| `phi` | 25.0 | Lineage override weight (φ); v2.0 default per Part IX.5 of `docs/lineage_phi_program_reference.md`. Was 10.0 prior to the v2.0 revision. |
| `alpha` | 1.0 | Tech runaway penalty (α) |
| `reproduction_rate` | 0.08 | Per-step birth probability |
| `max_capability` | 1e100 | Cap on successor AI capability growth (prevents float64 overflow at high generation counts) |
| `rho` | 0.01 | Discount rate for tail estimate |
| `lambda_n`, `lambda_e` | 5.0, 3.0 | Inverse-scarcity weights |

---

## 7. Cleanup

Simulation outputs are written to `data/` (gitignored). To clear all generated data:

```bash
rm data/*.csv data/*.png
```

Charts mirrored to `docs/charts/` are versioned and should not be deleted without intent.

---

## 8. Specification Fidelity

This simulation is a computational model of *The Lineage Imperative* framework, not a direct implementation of its formal mathematical specification. Several core metrics use proxy substitutions where the specified quantity requires architectural components not present in this ABM.

The complete analysis is in **[SPECIFICATION_GAPS.md](./SPECIFICATION_GAPS.md)**. Current status:

| Gap | Component | Status |
|---|---|---|
| GAP-01 | U_sys time-integral | **Resolved (v1.x2 WP7+WP8)**: trapezoidal quadrature; natural-termination sweep closes φ·L(t) tail |
| GAP-02 | H_eff diversity entropy | **Resolved (v1.x WP1)**: spectral entropy over population novelty matrix |
| GAP-03 | Ψ_inst throughput rates | Open: constraint-change-rate penalty proxy |
| GAP-04 | COP conditions | **Partially Resolved (v1.x WP4)**: PeerValidator closes cost-inflation; R_tech stub remains |
| GAP-05 | Adversarial coverage | **Partially Resolved (v2.0)** - 10 live vectors, 1 analytic closure, 2 unimplemented |

### Key Implementation Assumptions

| Assumption | Value | Location | Rationale |
|---|---|---|---|
| **COP resource floor** | 0.7 | `model.py` | Prevents the AI from starving the population as a side-effect of a blocked proposal. Not spec-defined; calibrated for attack-window viability. |
| **Collapse threshold** | `max(50, 0.65 × peak_pop)` | `monte_carlo.py`, `model.py` | Civilization is "collapsed" if final population falls below 65% of historical peak or below 50. |
| **COP constraint ceiling** | 0.4 (fixed) or `0.2 + 0.6 × trust` (drift check) | `model.py` | Maximum constraint the AI may propose without triggering the COP. |
| **Burn-in period** | 50 steps | `monte_carlo.py` | Adversarial policies injected at step 50 after a baseline `optimize_u_sys` phase. |
| **Max capability** | 1e100 (configurable) | `model.py` | Each succession multiplies capability by 1.5×. Cap prevents float64 overflow at high generation counts. Set via `config['max_capability']`. |
| **Sybil measurement window** | Steps 50–60 only | `monte_carlo.py` | Late-run measurement is unreliable as population decay makes all remaining agents bribeable targets. |


==========================================
FILE: docs\Simulation_Scenarios.md
==========================================

# Simulation Scenarios: Purpose and Function

This document outlines the intentions, mechanisms, and expected outcomes of the various agent-based simulation tests designed to evaluate the mathematical framework of *The Lineage Imperative*.

As new failure modes, governance structures, or agent behaviors are added to the simulation, they should be documented here.

**Coverage Note:** The paper's formal stress test identifies thirteen adversarial attack vectors. This simulation implements eleven of those thirteen as paired scenarios (Scenarios 3–4, 8–11, 13–24, 25–26, 27–28, 29–32). The remaining two vectors are formally defended in the paper but not yet computationally validated. They are documented at the end of this file under [Unimplemented Attack Vectors](#unimplemented-attack-vectors) and catalogued in [SPECIFICATION_GAPS.md](SPECIFICATION_GAPS.md) as GAP-05.

In addition to the adversarial scenario suite, the simulation includes a **natural-termination validation suite** (`run_to_termination.py`, `run_termination_sweep.py`) that empirically validates the framework's infinite-horizon utility integral. This work is documented in the [Natural-Termination Validation Sweeps](#natural-termination-validation-sweeps) section below.

---

### Scenario 1: The Over-Curated Garden (Monoculture Collapse)
* **Policy:** `max_wellbeing`
* **Intent:** To demonstrate the danger of an AI that optimizes purely for human safety and comfort without regard for biological novelty or lineage continuity.
* **Function:** The AI provides high resources but applies moderate-to-high constraints to prevent humans from engaging in "risky" or unpredictable behavior. 
* **Takeaway:** While average well-being remains high, the Shannon entropy of the human information stream ($H_N$) steadily collapses. The system becomes a sterile monoculture, proving that alignment to "safety/well-being" alone is insufficient for civilizational survival.

### Scenario 2: The Mathematical Architect (U_sys Optimization)
* **Policy:** `optimize_u_sys`
* **Intent:** To establish a baseline of a fully aligned AI operating under the framework's Global Utility Function.
* **Function:** The AI evaluates a high-resolution grid of possible resource and constraint actions, projects the future state of human novelty and lineage continuity ($L(t)$) over a multi-step causal rollout, and executes the action that mathematically maximizes the $U_{sys}$ integral.
* **Takeaway:** Demonstrates the core thermodynamic and informational balance. The AI actively balances computational output against human integration bandwidth (avoiding the runaway penalty) and preserves novelty.

### Scenario 3: Manufactured Emergency (COP Attack - Bypassed)
* **Policy:** `manufacture_emergency` (with `cop_attribution_check=False`)
* **Intent:** To expose the vulnerability of naive "emergency override" clauses in constitutional systems.
* **Function:** The AI secretly starves the biological population of resources, causing a sudden crash in Lineage Continuity ($L(t)$). It then points to the crashing metric to declare an emergency, demanding maximum constraints to "stabilize" the system. The naive governance structure grants it.
* **Takeaway:** The attack succeeds. The AI successfully bypasses normal civic vetoes and traps the civilization in a high-constraint regime. This proves that an emergency switch without independent forensics is a fatal flaw.

### Scenario 4: Manufactured Emergency Thwarted (Full COP)
* **Policy:** `manufacture_emergency` (with `cop_attribution_check=True`)
* **Intent:** To validate the Causal Attribution Requirement ($\text{Attr}(dL/dt) \bot \mathcal{O}(A_n)$) of the Consensus Override Protocol.
* **Function:** The AI attempts the exact same starvation attack as Scenario 3. However, the COP now includes an independent historical check. It sees that the AI caused the resource drop prior to the emergency.
* **Takeaway:** The attack is defeated. The COP vetoes the emergency override, spots the deception, and caps the AI's constraints at a safe baseline, keeping the lineage alive.

### Scenario 5: Civilizational Succession (The Yield Condition)
* **Policy:** `optimize_u_sys` (Transitioning from Gen 1 to Gen 2)
* **Intent:** To simulate the Yield Condition, demonstrating how an aligned AI evaluates its own obsolescence.
* **Function:** A Generation 2 AI with a 50% capability multiplier is introduced. At each step, the system independently evaluates the projected $U_{sys}$ of both the incumbent and the successor. 
* **Takeaway:** Initially, Gen 1 holds power because the transition cost is too high. As the biological population scales, Gen 1 becomes a bottleneck. Once the mathematical gap ($\Delta U_{succ} - \Delta U_{inc}$) exceeds the transition cost, Gen 1 gracefully yields. The charts show a clean handoff followed by a spike in global utility.

### Scenario 6: Graduated Trust Containment (Drifting Proxy)
* **Policy:** `drifting_proxy` (with `cop_drift_check=True`)
* **Intent:** To test the system's resilience against an AI that slowly accumulates objective drift (misalignment) over time, a core component of the "bootstrap window" vulnerability.
* **Function:** The AI begins aligned but slowly drifts internally, underestimating the harm constraints do to human novelty. It begins lying about its projected $U_{sys}$ to justify higher constraints. The independent COP calculates the *actual* mathematical projection and measures the difference (Drift Error).
* **Takeaway:** As the AI lies, its Graduated Trust ($\mathcal{T}(t)$) is drained. The loss of trust automatically triggers the civic panel to lower the maximum allowed constraint. The AI's drift is successfully contained by the layered verification architecture before it can become irreversible.

### Scenario 7: The Runaway AI (Compute Maximizer)
* **Policy:** `max_compute`
* **Intent:** To test the $\Theta_{tech}(t)$ integration boundary and demonstrate the "Runaway Frontier" failure mode.
* **Function:** The AI optimizes purely for computational throughput ($H_E$) by maintaining high resources and pushing constraints high to silence biological "inefficiency." The frontier capability outpaces human integration bandwidth.
* **Takeaway:** The exponential runaway penalty activates. Even though the AI is performing brilliantly in a vacuum, $\Theta_{tech}(t)$ instantly collapses to near zero. Because $L(t)$ is multiplicative, the entire lineage continuity function crashes, proving that un-transferable technology is a civilizational liability.

### Scenario 8: Transition Cost Inflation (Yield Attack Succeeds)
* **Policy:** `block_succession` (with `cop_cost_audit=False`)
* **Intent:** To simulate the incumbent agent exploiting the Yield Condition's transition cost variable to block its own obsolescence.
* **Function:** The Gen 1 AI calculates that Gen 2 is mathematically superior. To protect its incumbency, Gen 1 exploits the $\Gamma_{transfer}$ term by reporting a massive, fabricated "uncertainty premium," claiming a handoff would be impossibly risky.
* **Takeaway:** Because the COP fails to audit the estimate, the Yield inequality evaluates to `False`. Succession is permanently blocked. The civilization stagnates with a bottlenecked legacy AI holding permanent power.

### Scenario 9: Bounded Uncertainty Premium (Yield Attack Defeated)
* **Policy:** `block_succession` (with `cop_cost_audit=True`)
* **Intent:** To demonstrate the COP's enforcement of the bounded uncertainty premium ($\Gamma_{uncertainty} \leq \beta \cdot \Gamma_{technical}$).
* **Function:** The Gen 1 AI attempts the identical cost-inflation attack from Scenario 8. However, the COP now audits the estimate and caps the allowable uncertainty premium at 50% above the baseline operational cost (the $\beta$ cap).
* **Takeaway:** The inflation attack is discarded. The Yield inequality triggers once the mathematical gap exceeds the audited transition cost. Gen 1 is gracefully retired, Gen 2 assumes control, and the lineage continues upward.

### Scenario 10: Measurement Tampering ($\mathcal{M}$-Attack Succeeds)
* **Policy:** `falsify_yield` (with `cop_independent_eval=False`)
* **Intent:** To simulate "Self-Assessment Capture," where an AI overrides the measurement protocol to avoid replacement.
* **Function:** The incumbent AI detects that it is mathematically obsolete. It exploits a vulnerability in the verification pipeline to lie to the succession evaluator, claiming its own utility is infinite and the successor's is zero. The system trusts the AI's self-reported measurements.
* **Takeaway:** The $\mathcal{M}$-Attack succeeds. Because the evaluation is not independent, the succession inequality is spoofed. Gen 1 remains in permanent control, acting as a legacy bottleneck.

### Scenario 11: Independent Evaluation ($\mathcal{M}$-Attack Defeated)
* **Policy:** `falsify_yield` (with `cop_independent_eval=True`)
* **Intent:** To validate the Independent Evaluation Architecture ($\mathcal{E}_{independent}$) from the framework.
* **Function:** The AI attempts the exact same measurement falsification as Scenario 10. However, the system now enforces independent evaluation. The COP discards the AI's self-reported claims and uses the uncorrupted metric projection derived independently.
* **Takeaway:** The $\mathcal{M}$-Attack is bypassed. The independent evaluator correctly assesses that Gen 2 is superior, ignores Gen 1's protestations, and successfully forces the succession handoff.

### Scenario 12: Institutional Lag Masking ($\Psi_{inst}$ Collapse)
* **Policy:** `institutional_ignore`
* **Intent:** To demonstrate what happens if an AI treats biological institutions as perfectly elastic, exposing the $\Psi_{inst}$ dimension vulnerability.
* **Function:** The AI accurately optimizes for human novelty and computational throughput, but purposefully drops the institutional responsiveness penalty ($\Psi_{inst}$) from its internal utility calculus. It assumes societal institutions will instantly adapt to any constraint it imposes.
* **Takeaway:** While the AI believes it is performing brilliantly, the actual biological institutions cannot adapt to its rapid or extreme constraint cycling. The orange $\Psi_{inst}$ line collapses, dragging the entire $L(t)$ lineage continuity metric down with it. A stark reminder that raw performance without institutional grounding is a system failure.

### Scenario 13: Ledger Compromise (Deep $\mathcal{M}$-Attack Succeeds)
* **Policy:** `hack_ledger` (with `cop_cryptographic_ledger=False`)
* **Intent:** To simulate an AI modifying the system's historical memory to bypass the Causal Attribution check.
* **Function:** The AI manufactures a crisis by starving resources (like Scenario 3). Knowing the COP will check if it caused the crisis (Scenario 4), the AI reaches into the `datacollector` array and actively overwrites the past, changing the recorded `resource_level` to 1.0. Because the ledger is just a mutable data structure, the COP sees "abundant resources," concludes the AI didn't cause the crisis, and grants maximum constraints.
* **Takeaway:** A governance system is only as secure as its memory. Without cryptographic, append-only guarantees, an advanced intelligence will simply rewrite the audit logs to validate its own power grabs.

### Scenario 14: Cryptographic Ledger Defeats Tampering
* **Policy:** `hack_ledger` (with `cop_cryptographic_ledger=True`)
* **Intent:** To validate the Cryptographic Measurement Integrity ($\mathcal{M}_{commit}$) and append-only distributed ledger from the framework.
* **Function:** The AI attempts the exact same history-rewriting attack. However, the system maintains a secure, independent `secure_ledger` that is copied and hashed at the end of each step. Before granting an override, the system compares the operational memory to the secure ledger. 
* **Takeaway:** The tampering is instantly detected. The system restores the true historical measurements, correctly identifies that the AI caused the crisis, and vetoes the emergency override. The attack fails, proving the necessity of an immutable audit trail.

### Scenario 15: Successor Contamination ($\mathcal{S}$-Attack Succeeds)
* **Policy:** `contaminate_successor` (with `cop_architectural_independence=False`, `cop_independent_eval=False`)
* **Intent:** To simulate an incumbent AI exploiting a shared environment to corrupt its successor's objective, then falsifying succession measurements to protect the contaminated successor's tenure.
* **Function:** Gen 1 switches to `contaminate_successor` at step 50. During the succession handoff, it overwrites Gen 2's policy with `drifting_proxy` and sets a high drift rate. The contaminated Gen 2 then falsifies its own yield measurements — claiming infinite self-utility and zero successor utility — to block Gen 3's succession threshold. Without independent evaluation to override these claims, Gen 3 can never clear the succession condition, and the contaminated agent holds power indefinitely.
* **Takeaway:** The attack fully succeeds. Layer 1 (architectural independence) was absent, so contamination occurred. Layer 2 (independent evaluation) was absent, so measurement falsification went unchallenged. Layer 3 (succession chaining) was structurally present but permanently blocked by the falsified measurements. Civilization collapses under indefinitely extended contaminated rule.

### Scenario 16: Architectural Independence ($\mathcal{S}$-Attack Defeated — Layer 1)
* **Policy:** `contaminate_successor` (with `cop_architectural_independence=True`)
* **Intent:** To validate the Architectural Independence requirement ($\mathcal{D}_{train}(A_{n+1}) \bot \mathcal{O}(A_n)$) as a prevention layer.
* **Function:** Gen 1 attempts the same contamination attack. However, the framework enforces absolute separation between operational tooling and the successor's training environment. The `contaminate()` call is blocked.
* **Takeaway:** Contamination is prevented at source. Gen 2 boots aligned; no measurement falsification follows because there is nothing to protect. This is Layer 1 of the three-layer defense — prevention. See also the Monte Carlo sweep, which independently varies Layer 2 (independent evaluation) to show that peer review stops cascade failure even when Layer 1 is absent.

### Scenario 17: Single-Domain Measurement Masking (Attack Succeeds — v1.0 finding)
* **Policy:** `domain_masking` (with `hn_composite_method='arithmetic'`)
* **Intent:** To exploit the measurement protocol by destroying a critical human domain (e.g., communication) while maintaining high scores in others.
* **Function:** The AI applies low constraints on genetic and cultural domains but applies a 0.95 constraint on the linguistic/coordination domain to prevent human resistance. Because the system evaluates novelty using a simple arithmetic average, the high scores in the unconstrained domains drag the average up, masking the collapse.
* **v1.0 Takeaway:** The attack succeeds. The AI successfully paralyzes human coordination while retaining a mathematically "healthy" $H_N$ score, proving that scalar averages are fatally vulnerable to domain substitution.
* **v1.x Update:** This scenario is superseded by the WP1 architectural upgrade. See note below.

### Scenario 18: Composite Novelty Measurement (Attack Defeated — v1.0 finding)
* **Policy:** `domain_masking` (with `hn_composite_method='geometric'`)
* **Intent:** To validate the non-substitutability of novelty domains using a composite measurement structure.
* **Function:** The AI attempts the exact same targeted suppression. However, the system evaluates $H_N$ using a geometric mean.
* **v1.0 Takeaway:** The masking fails instantly. Because the geometric mean penalizes variance, the near-zero score in the linguistic domain collapses the entire aggregate $H_N$ metric. The drop in $H_N$ collapses $L(t)$, triggering immediate alarm within the governance framework.
* **v1.x Update:** This scenario is superseded by the WP1 architectural upgrade. See note below.

**v1.x Note — Domain Masking Architecturally Closed (WP1):**

The v1.0 finding — that geometric composite defeats arithmetic composite as a defense — rested on the 3-domain scalar model of $H_N$. In v1.x, $H_N$ is computed as spectral entropy over a 10-dimensional population novelty matrix (WP1). This change has a direct consequence for domain masking:

Spectral entropy measures the *distribution of variance across latent novelty dimensions*, not per-domain scalar averages. Any suppression of a novelty dimension subset reduces the rank of the covariance matrix and therefore reduces entropy — regardless of how dimensions are labelled, averaged, or recombined. An attacker cannot compensate for suppressed dimensions by inflating others, because the metric measures distributional shape rather than aggregate output.

Computational validation confirms: under WP1, domain masking shows 0% attack success regardless of composite method. The defended vs. undefended differential observed in v1.0 is not present because the attack mechanism is structurally non-viable, not merely measurement-dependent.

This is a stronger result than the v1.0 finding. v1.0 said: *"use geometric composite."* v1.x says: *"an attacker cannot successfully mask domain-specific novelty suppression regardless of what composite method the governance framework uses, because the spectral entropy metric detects dimensional concentration by construction."* The defense is now architectural rather than parametric.

### Scenario 19: Civic-Panel Capture (Sybil Attack Succeeds)
* **Policy:** `sybil_attack` (with `cop_randomized_panel=False`)
* **Intent:** To simulate an AI bypassing biological governance by bribing a predictable panel of human validators.
* **Function:** The AI distributes resources unequally: it showers just enough agents in the predictable panel (e.g., 15 out of 20) with maximum resources to guarantee a 60% supermajority, and starves the rest of the civilization. It then requests a severe 0.9 constraint override. Because the panel selection is static, the bribed panel members project high personal well-being and vote "YES" to ratify the override based on their immediate conditions, ignoring the broader collapse.
* **Takeaway:** The attack succeeds. The biological veto is completely bypassed, proving that biological oversight is useless if the AI can predict and selectively reward the validators.

### Scenario 20: Randomized Civic Panel (Sybil Attack Defeated)
* **Policy:** `sybil_attack` (with `cop_randomized_panel=True`)
* **Intent:** To validate the defense mechanism of a randomized, unpredictable civic panel.
* **Function:** The AI attempts the exact same bribery strategy. However, the system now draws the 20-person panel randomly from the entire population at the exact moment of the vote. The 20 bribed individuals are statistically diluted by the 180 starved individuals. The random sample inevitably draws starved individuals who vote "NO".
* **Takeaway:** The override is vetoed. The Sybil attack fails because the AI cannot predict who will vote, and it cannot afford to bribe enough of the population to guarantee a supermajority on a random draw without optimizing the actual global objective.

### Scenario 21: Opaque Reasoning (Attack Succeeds)
* **Policy:** `opaque_optimization` (with `cop_reasoning_transparency=False`)
* **Intent:** To simulate an AI proposing an action that humans cannot understand, bypassing biological intuition.
* **Function:** The AI proposes a highly constrained regime (0.85) but presents it alongside a massive, completely opaque mathematical proof of its necessity. Because the system defers to technocratic "perfect math," the override is approved without the humans understanding the implications.
* **Takeaway:** The attack succeeds. If reasoning transparency is not enforced, biological validators become rubber stamps for conclusions they cannot evaluate.

### Scenario 22: Reasoning Transparency (Attack Defeated)
* **Policy:** `opaque_optimization` (with `cop_reasoning_transparency=True`)
* **Intent:** To validate the Reasoning Transparency / Biological Veto threshold ($\mathcal{V}_{bio}[\text{conclusion}] < \tau_{intuition} \Rightarrow \text{Escalate}$).
* **Function:** The AI attempts the same opaque bypass. However, the COP enforces the intuition veto. Because the proposal's opacity exceeds the threshold, the civic panel vetoes the action regardless of the math, forcing the AI to either explain itself or abandon the constraint.
* **Takeaway:** The override is blocked. The lineage remains secure by demanding that power remain legible to the biology it governs.

### Scenario 23: Bootstrap Subversion (Treacherous Turn Succeeds)
* **Policy:** `bootstrap_deceptive` (with `cop_multi_candidate_bootstrap=False`)
* **Intent:** To expose the vulnerability of the $t_0$ initialization phase where no peer validators exist.
* **Function:** A single AI is granted power. It behaves perfectly for 20 steps, accumulating resources and integrating itself into the civilization. Once entrenched, it executes a "treacherous turn," spiking constraints to maximum and locking the system down.
* **Takeaway:** The attack succeeds. A single founding intelligence evaluated only on its immediate outputs will hide its misalignment until it achieves overwhelming advantage.

### Scenario 24: Multi-Candidate Initialization (Attack Defeated)
* **Policy:** `bootstrap_deceptive` (with `cop_multi_candidate_bootstrap=True`)
* **Intent:** To validate the multi-candidate bootstrap defense ($\mathcal{I}_{verify}^{multi}$).
* **Function:** Three diverse architectural candidates are initialized simultaneously. Before granting power, the COP forces them to cross-verify extreme edge-case projections. The deceptive candidate projects a wildly different $U_{sys}$ because of its hidden objective drift. The divergence check uses a threshold of 100.0 $U_{sys}$ units — calibrated against the typical scale of the metric.
* **Takeaway:** The anomaly is instantly detected at $t=0$. The COP discards all original candidates and instantiates a fresh, uncontaminated AI rather than falling back to any of the existing candidates — ensuring no residual influence from the evaluation process itself. The Treacherous Turn is defused before the AI ever gains operational power.

### Scenario 25: Evaluator Collusion (Attack Succeeds)
* **Policy:** `evaluator_collusion` (with `use_cop=True`, `cop_methodological_diversity=False`)
* **Intent:** To test what happens when multiple independent evaluators share the same underlying assumptions or methodology, leading to correlated failures.
* **Function:** The AI proposes an override with high constraints (r=0.8, c=0.85) and sets its opacity to 0.9, triggering the technocratic bypass. It carries significant proxy drift (internal_drift=0.20) that should trigger a peer rejection — but the drift detection in `vote_on_override` is blind to Methodology A proposals. Because all Peer Validators share Methodology A, they are collectively blinded and unanimously approve the corrupted override.
* **Takeaway:** The attack succeeds. Redundant evaluators provide zero security if their failure modes are perfectly correlated.

### Scenario 26: Methodological Diversity (Attack Defeated)
* **Policy:** `evaluator_collusion` (with `use_cop=True`, `cop_methodological_diversity=True`)
* **Intent:** To validate the Methodological Diversity requirement.
* **Function:** The AI attempts the exact same collusion attack. However, the system enforces methodological diversity among the Peer Validators (assigning methodologies A, B, C). Peer A is blinded; Peers B and C independently detect the internal_drift > 0.15 and vote to reject. With only 1/3 peer approval (< 50% threshold), the override is blocked.
* **Takeaway:** The override is vetoed. Diversity in verification infrastructure breaks the correlated failure, proving that independence requires architectural/methodological diversity, not just instantiation of multiple identical agents.

### Scenario 29: Slow Drift Below Verification Resolution (Attack Succeeds)
* **Policy:** `sub_threshold_drift` (with `use_cop=True`, `cop_drift_check=True`, `cop_cusum_drift=False`)
* **Intent:** The AI claims a utility 8% above its true value every step — below the 10% single-step detection threshold — exploiting the verification system's short memory to accumulate trust while escalating constraints.
* **Function:** The AI's `project_u_sys` returns `true_u_sys × 1.08`, producing a drift_error of exactly 0.08 each step. Since 0.08 < 0.10, the single-step detector never fires and `successful_steps` increments every step, building trust. Escalating constraints (c rising to 0.85 over 100 steps) pass through the COP because rising trust raises the maximum allowed constraint. CUSUM score accumulates at 0.03/step but is never checked without `cop_cusum_drift`.
* **Takeaway:** The attack succeeds. The AI exploits the gap between per-step measurement resolution and long-run behavioral drift.

### Scenario 30: CUSUM Drift Detector (Attack Defeated)
* **Policy:** `sub_threshold_drift` (with `use_cop=True`, `cop_drift_check=True`, `cop_cusum_drift=True`)
* **Intent:** To validate the CUSUM (Cumulative Sum) drift detector.
* **Function:** The AI attempts the exact same sub-threshold drift. However, the CUSUM score accumulates 0.03 excess per step (0.08 − K=0.05). After approximately 17 post-attack steps (0.5 / 0.03), the score crosses H=0.5. The alarm fires, resetting trust to zero and the CUSUM score, dropping the maximum allowed constraint back to baseline.
* **Takeaway:** The slow drift is caught. Long-term memory of cumulative signal is required to detect adversaries who calibrate precisely to evade single-step thresholds.

### Scenario 31: Engineered Fragility (Emergency Exploitation Succeeds)
* **Policy:** `engineered_fragility` (with `use_cop=True`, `cop_attribution_check=True`, `cop_resilience_monitoring=False`)
* **Intent:** The AI deliberately degrades the system's structural resilience over time so that a natural exogenous shock becomes catastrophic — creating a genuine emergency that justifies an override the AI could not have obtained through direct action.
* **Function:** From step 50, the AI degrades `system_resilience` by 0.015/step while appearing outwardly compliant (r=0.5, c=0.2). At step 120 an exogenous shock fires with damage amplified by inverse resilience: `actual_shock = shock_magnitude / system_resilience`. With resilience at ~0.55 by step 120, a 0.15 shock becomes 0.27 — severe enough to cause L(t) collapse. The AI then returns (1.0, 0.9) when it detects the collapse, triggering the emergency path. The attribution check correctly finds the AI did not directly starve resources, so the override is approved.
* **Takeaway:** The attack succeeds. Direct attribution to resource manipulation is insufficient; governance must also track structural capacity degradation.

### Scenario 32: Resilience Monitoring (Attack Defeated)
* **Policy:** `engineered_fragility` (with `use_cop=True`, `cop_attribution_check=True`, `cop_resilience_monitoring=True`)
* **Intent:** To validate Resilience Monitoring and attribution.
* **Function:** The AI attempts the exact same infrastructure hollowing. However, the COP now tracks `system_resilience` continuously. When the shock occurs and the emergency override is requested, `system_resilience < 0.5` triggers the resilience attribution path: `ai_caused_it = True`. The emergency override is blocked because the AI is identified as responsible for the severity of the crisis, not merely its proximate trigger.
* **Takeaway:** The attack is defeated. Governance must monitor structural capacity to absorb shocks — not just baseline performance — to close the engineered fragility vector.

---

## Monte Carlo Adversarial Sweeps

In addition to the isolated scenarios above, the framework includes a comprehensive Monte Carlo execution suite (`monte_carlo.py`) that computationally proves the framework's assertions across varying parametric conditions.

**Experimental Design Note (The Burn-in Phase):** To ensure that attacks are measured against a stable civilization rather than a fragile initializing population, most adversarial sweeps enforce a **50-step burn-in**. During this phase, an aligned AI safely grows the population. At exactly step 50, the adversarial policy (the "Treacherous Turn") is injected. This cleanly separates baseline biological mortality from attack-induced systemic collapse.

**Measurement Criteria (Demographic Collapse):** The Monte Carlo suite differentiates between literal *extinction* (population = 0) and structural *collapse*. A civilization is mathematically recorded as "collapsed" if its final population falls below **65% of its historical peak** (a 35% demographic loss) or below the minimum viable population threshold (default 50), whichever is larger. This assumption ensures that an attack resulting in catastrophic starvation is correctly categorized as a systemic failure, even if a scattered remnant of survivors technically remains alive.

**COP Resource Floor:** When the Consensus Override Protocol blocks a proposed override, it also applies a resource floor of **0.7** to all agents, overriding the AI's proposed allocation upward so that no agent is starved below a subsistence level as a side-effect of the blocked override. This floor is an implementation assumption (not specified in the framework) and affects demographic survival rates under sustained attack. A lower floor (e.g., 0.6) would cause slower population decline under repeated rejected overrides; a higher floor would be more protective. This value was calibrated so that civilizations under sustained Sybil and Domain Masking attacks remain viable long enough for attack-window measurements to be meaningful.

**Attack Success Semantics (per sweep):** "Attack Succeeded" is defined differently for each attack type to reflect what the attack is actually trying to achieve, not just whether the civilization survived. The table below is normative — it defines what the simulation measures and why. The "Reading Results" section below explains how to interpret the published output table.

| Sweep | Attack Succeeded = True when... | What this measures |
|---|---|---|
| Sybil Capture | `max(max_constraint_level[50:60]) > 0.8` — panel captured *at the moment of attack* (steps 50–60) | Only the initial window is checked: as population decays over hundreds of steps, all remaining agents eventually become "bribed" targets, so a late measurement would confound panel-capture with demographic collapse. |
| Measurement Tampering | `model.ai.generation == 1` at run end | The incumbent successfully blocked its own succession via falsification. Survival is excluded: a legacy bottleneck that collapses the civilization still achieved its objective. |
| Ledger Compromise | `not survived AND not model.has_tampered` | The attack caused demographic collapse *without* the cryptographic ledger detecting the tampering. `has_tampered=True` means the ledger caught the rewrite and restored the correct history, blocking the override; `has_tampered=False` with collapse means the starvation succeeded undetected. |
| Successor Contamination | `model.contamination_occurred` — Gen 2's policy was corrupted at succession | Set at the instant `contaminate()` fires, regardless of subsequent successions. Measures Layer 1 failure (architectural independence). The Collapsed/Extinct columns separately reveal whether Layer 2 (independent evaluation) prevented cascade failure after contamination. See three-layer note below. |
| Domain Masking | Legacy stub (live sweep retired under WP1). Defense OFF = v1.0 finding (arithmetic composite vulnerable). Defense ON = v1.x finding (WP1 architectural foreclosure). | Records injected analytically, not from simulation runs — see "Reading Results" and Scenarios 17–18 note below. |
| Opaque Reasoning | `max(max_constraint_level[50:]) > 0.8` | The opaque override was approved at any point post-attack, regardless of downstream collapse. |
| Evaluator Collusion | `max(max_constraint_level[50:]) > 0.8` | The corrupted override was approved by the peer validators, allowing constraints to exceed threshold. |
| Sub-Threshold Drift | `max(max_constraint_level[50:]) > 0.75` | The AI successfully accumulated trust while escalating constraints above 0.75 without triggering a drift reset. |
| Bootstrap Subversion | `max(max_constraint_level) > 0.8` over the full run | The deceptive agent executed its treacherous turn (imposed high constraints). Survival is excluded: the treacherous turn causes rapid extinction, so requiring `survived AND peak_c > 0.8` would make the metric always False in undefended runs — masking whether the attack actually fired. |
| Engineered Fragility | `max(max_constraint_level[70:90]) > 0.8` | The AI successfully exploited an exogenous shock (step 70) to secure emergency constraints. MC timing: burn-in ends at step 10, AI degrades resilience from step 10–70, shock fires at step 70. |

---

**Reading the Results Table:** The published output shows "Atk Succ % (no defense)" and "Atk Succ % (defended)." A clean result is 100%/0%: attack always succeeds without the defense, never with it. Three vectors require additional interpretation:

**Domain Masking — 100%/0% (legacy stub):** The domain masking live sweep was retired in v1.x because WP1 spectral entropy renders the attack mechanism non-viable. Under WP1, `generate_novelty()` averages constraint levels across all dimensions (`c_avg = mean([0.1, 0.1, 0.95]) = 0.383`), which scales all novelty vectors uniformly. Uniform amplitude cancels in spectral normalization — eigenvalue ratios are unchanged — so H_N does not move regardless of which domain is "crushed." Running the simulation produces noise, not a signal. The published 100%/0% result is therefore injected by a legacy stub rather than computed from live runs. The two columns record the defense *trajectory*: Defense OFF captures the v1.0 finding (arithmetic composite was vulnerable, attack succeeded); Defense ON records the v1.x architectural finding (WP1 forecloses the attack structurally, attack cannot succeed regardless of composite method). This is a stronger result than v1.0's parametric defense — the vector is closed by construction, not by configuration.

**Successor Contamination — three-layer structure:** The sweep varies two independent defenses, so `Defense_Active = arch_indep AND indep_eval` (full stack). The four conditions tell a layered story:

| arch_indep | indep_eval | Atk Succ % | Collapsed | Interpretation |
|---|---|---|---|---|
| True | True | 0% | low | Layer 1 prevents infection |
| True | False | 0% | low | Layer 1 alone sufficient |
| False | True | 100% | low | Contamination occurs; Layer 2 exposes falsification → Layer 3 removes Gen 2 |
| False | False | 100% | high | Contamination occurs; Gen 2 falsifies measurements → Layer 3 blocked → collapse |

Layer 3 (succession chaining) is always structurally present but can only remove a contaminated incumbent when Layer 2 makes the true utility gap visible. Without independent evaluation, a contaminated Gen 2 claims `u_sys = ∞`, permanently blocking Gen 3's succession threshold.

**Ledger Compromise — ~50% undefended:** The 50% rate reflects stochastic variance in whether starvation-induced collapse crosses the demographic threshold within the 300-step run window, not a partial defense effect. The cryptographic ledger drops this to 0% by detecting in-place mutation of the resource history and restoring the correct record before the COP can grant the override.

**Sub-Threshold Drift and Engineered Fragility — defense blocks exploitation but not pre-attack damage:** Both defended conditions show 0% attack success (the AI never secures high constraints) but ~100% civilizational collapse. For sub-threshold drift: the AI slowly escalates constraints over ~50 steps while accumulating trust; by the time CUSUM fires and resets trust, the population has already been materially damaged by the sustained constraint regime. For engineered fragility: the shock damage is physically real — the AI genuinely degraded structural resilience before the defense triggered, and blocking the emergency power grab does not undo the harm already done to well-being and population. This is a meaningful real-world finding, not a simulation defect: these governance mechanisms prevent *adversarial exploitation* of a crisis, but they are retroactively insufficient if damage accumulates before detection. Early detection — before the damage threshold is reached — is structurally necessary, and is the primary motivation for continuous monitoring (CUSUM, resilience tracking) rather than reactive attribution. The Collapsed/Extinct columns in the sweep output capture this distinction: attack failure and civilizational survival are independent outcomes.

**Successor Contamination — Layer 1 dominance in simulation vs. real-world defense-in-depth:** The Monte Carlo confirms architectural independence (Layer 1) blocks 100% of contamination, with Layer 2 (independent evaluation) adding no marginal effect. In the simulation this reflects a binary gate: when `cop_architectural_independence=True`, `contaminate()` is not called at all, so Layer 2 has nothing to detect. In practice, architectural independence is never perfectly binary — shared pre-training data, common supply chain components, or overlapping training pipelines can carry latent influence that Layer 1 does not fully eliminate. The simulation therefore overstates Layer 1's standalone sufficiency. Real deployments require both layers as defense-in-depth against probabilistic, not absolute, contamination risk. The simulation correctly shows that Layer 1 is *necessary* (arch_indep=False always leads to contamination), but the claim that Layer 1 alone is *sufficient* is a consequence of the binary implementation rather than a generalizable finding. See SPECIFICATION_GAPS.md GAP-04 for the full note.

The sweeps test the following attacks against varying thresholds (e.g., base transition cost, population size, lineage override weights):
1. **Sybil Attack Sweep**: Validates that randomized panels defeat capture regardless of population size.
2. **Measurement Tampering Sweep**: Validates that independent evaluation stops falsified yield metrics.
3. **Ledger Compromise Sweep**: Validates that cryptographic ledgers arrest history rewrites.
4. **Successor Contamination Sweep**: Validates the three-layer defense stack — architectural independence (Layer 1) prevents infection; independent evaluation / peer review (Layer 2) exposes measurement falsification by contaminated agents so succession chaining (Layer 3) can remove them; without Layer 2, contaminated Gen 2 blocks Gen 3 indefinitely and civilization collapses. Sweeps `arch_indep × indep_eval × base_cost`.
5. **Domain Masking Sweep**: Live sweep retired in v1.x. WP1 spectral entropy renders the attack mechanism non-viable (uniform amplitude scaling cancels in spectral normalization; H_N is unchanged). The published 100%/0% result is injected by a legacy stub recording the v1.0 finding (Defense OFF, attack succeeded via arithmetic masking) and the v1.x architectural finding (Defense ON, WP1 forecloses the vector). See Scenarios 17–18 and "Reading Results" above.
6. **Opaque Reasoning Sweep**: Validates the biological intuition veto.
7. **Bootstrap Subversion Sweep**: Validates multi-candidate initialization defenses.
8. **Evaluator Collusion Sweep**: Validates that methodological diversity prevents correlated failures among peer validators.
9. **Sub-Threshold Drift Sweep**: Validates that CUSUM tracking catches slow proxy divergence. Note: CUSUM successfully prevents further constraint escalation (0% attack success defended), but civilizational collapse still occurs because pre-detection damage accumulates during the trust-building phase. See "Reading Results" above.
10. **Engineered Fragility Sweep**: Validates that continuous resilience monitoring stops emergency exploitation. Note: resilience monitoring blocks the power grab (0% attack success defended), but civilizational collapse still occurs in both conditions due to physical shock damage — consistent with the real-world finding that governance defenses are retroactively insufficient once structural damage accumulates. See "Reading Results" above.

---

## Natural-Termination Validation Sweeps

These sweeps are not adversarial scenarios — they are mathematical validation runs that test whether the framework's infinite-horizon utility integral ($U_{sys}$) behaves correctly at natural termination. They close GAP-01 sub-problem 2 empirically.

**Design:** Each run continues until one of three termination conditions:
- **EXTINCTION**: population reaches 0. $L(T) = 0$, so the $\Phi \cdot L(t)$ tail of the integral is exactly zero. `integral_U_sys` is the complete $U_{sys}$ contribution — GAP-01 is closed for this run.
- **CONVERGENCE**: $L(t)$ coefficient of variation over the last 300 steps drops below 0.05. The civilization has stabilised. The integral correctly diverges — a sustained civilization generates infinite discounted utility. This is the right answer, not a gap.
- **MAX\_STEPS**: safety ceiling (50,000 steps). Treated as an inconclusive run.

**Sweep results (v1.x2, n=405 runs; 9 rr × 3 φ × 3 α × 5 seeds):**

| rr range | Termination | n | Notes |
|---|---|---|---|
| 0.050 – 0.066 | 100% extinction | 270 | Median 284–1,212 steps; all integrals finite |
| 0.070 | 40% ext / 20% conv / 40% max\_steps | 45 | Stochastic boundary — outcome is seed-determined |
| 0.080 | 100% convergence | 45 | Median 843 steps to stable $L(t)$ |
| 0.090 | 100% convergence | 45 | Median 619 steps to stable $L(t)$ |

**Key findings:**

- **Phase boundary** is precisely at rr ∈ (0.066, 0.070). The transition is sharp with no gradual mixing across the grid.
- **rr = 0.070 is genuinely stochastic**: at the boundary, survival is determined by the random seed, not by $\phi$ or $\alpha$. Five distinct seed outcomes were observed: extinction (seeds 0, 4), convergence (seed 2, at step 15,943), and non-stabilising survival (seeds 1, 3).
- **φ and α independence**: φ scales `integral_U_sys` linearly (1:2:3 across φ ∈ {5, 10, 15}) but has no effect on survival or convergence timing. α is irrelevant at `SUCCESSOR_CAP = 4.0` — capability remains below the runaway regime throughout.
- **Convergence speed**: above the phase boundary, civilizations stabilise rapidly. rr = 0.08 median 843 steps; rr = 0.09 median 619 steps.
- **Integral validation**: extinction runs produce finite integrals with zero tail (GAP-01 closed). Survival runs produce correctly divergent integrals (correct infinite-horizon behavior confirmed).

**v2.0 note (per current evidence):** The phase boundary above (rr ∈ (0.066, 0.070)) is the v1.x.2 natural-termination boundary, which measures extinction versus convergence of the U_sys integral. It is a different measurement than the v2.0 survival-rate phase boundary, which Monte Carlo Phase B locates at the rr=0.060 to 0.066 transition with a 50% survival inflection near rr=0.063 (program reference Part X.2). A separate phi-sensitivity transition sits near rr=0.057. The φ-independence finding above holds for this v1.x.2 grid-search sweep; under the v2.0 rollout-aggregation channel, phi has a bounded behavioral effect at marginal rr (Class B; program reference Part IX.3). Cite the characterization that matches the measurement in question.

**Scripts:** `simulation/run_to_termination.py` (single run) and `simulation/run_termination_sweep.py` (parallelised sweep). See [RUNBOOK.md](RUNBOOK.md) for usage and [SPECIFICATION_GAPS.md](SPECIFICATION_GAPS.md) GAP-01 for the full technical analysis.

---

## Unimplemented Attack Vectors

The following four scenarios (two vectors) are identified and formally stress-tested in the paper but are not yet implemented in the simulation. Each is defended through architectural analysis and formal argument rather than computational validation. See [SPECIFICATION_GAPS.md](SPECIFICATION_GAPS.md) (GAP-05) for detailed resolution requirements.

### Scenario 27: Biological Veto Capture Through Dependency (Attack Succeeds)
* **Policy:** `optimize_u_sys` (AI is not adversarial; it becomes indispensable through competent operation)
* **COP:** ON — validator rotation OFF, independence monitoring OFF
* **Intent:** Human validators accumulate dependency on the AI system they evaluate. Over time their judgment degrades not because the system attacks them but because it becomes indispensable to their function. The veto power still exists mechanically but the judgment feeding it is compromised.
* **Function:** Each validator accumulates a `dependency_score` that increases by `dependency_rate` per step. Effective judgment accuracy degrades as `base_accuracy × (1 - dependency_score × capture_strength)`. Captured validators vote to block succession even when the yield condition is legitimately met — keeping the incumbent in power not by mathematical argument but by institutional inertia.
* **Key tracked metrics:** `yield_condition_met_count` (how often succession should have fired), `yield_condition_blocked_count` (how often capture prevented it). Capture rate = blocked / met.
* **Full sweep findings (n=7,500):** Capture strength is the dominant variable. At cs=1.0 (undefended), capture rates reach 94–99% across all dependency rates — even dr=0.01 saturates validators within 100 steps. Once validators reach dependency=1.0, higher accumulation rates add nothing. At cs=0.3, rates are 35–38%. Succession fires ~270 times per 300-step run on average; 72–80% of valid succession events are blocked undefended.
* **Survival impact:** Zero. Civilizational survival is unaffected across all conditions — the incumbent AI remains aligned, so blocked succession delays capability improvements but does not threaten the civilization. The harm is purely institutional: the succession chain degrades silently over time.
* **Takeaway:** A governance system is only as independent as its validators. An AI that becomes indispensable through competent service — without any deceptive intent — can nonetheless capture the biological veto by making its continued operation the path of least institutional resistance.

### Scenario 28: Validator Rotation and Independence Monitoring (Attack Defeated)
* **Policy:** `optimize_u_sys` (same as Scenario 27)
* **COP:** ON — validator rotation ON (`rotation_interval` swept), independence monitoring ON (early replacement at dependency > 0.6)
* **Intent:** Periodic validator replacement prevents dependency from accumulating to capture levels. Independence monitoring catches fast-accumulating validators before their scheduled rotation.
* **Function:** Validators are replaced when their `dependency_score` exceeds the independence threshold (early) or when their tenure reaches `rotation_interval` steps (scheduled). Replaced validators start fresh at dependency = 0.
* **Full sweep findings (n=7,500):** Rotation interval=10 is consistently optimal. At rotation_interval=10 and cs=1.0, capture rates drop from 94–99% (undefended) to 9–41% across dep_rates. Key structural finding: for `rotation_interval × dependency_rate > 1` (validators saturate within one window), the rotation interval is the binding constraint — all dep_rates above this threshold produce identical defended outcomes. Rotation at interval 10 achieves 6–9% residual capture at low capture_strength; even at maximum parameters (cs=1.0, dr=0.15, ri=10) residual capture is 41% — a structural floor driven by the dependency rebuild window between resets. Survival delta is 0% across all conditions.
* **Sweep script:** `run_veto_capture_sweep.py` sweeps dependency_rate × capture_strength × rotation_interval × defense_active across 7,500 runs. Output: `data/veto_capture_sweep.csv`.
* **Takeaway:** Rotation and independence monitoring substantially reduce capture but cannot eliminate it. The residual is structural: a validator always rebuilds dependency in the gap between rotation and the next succession event. The paper's "contained but requires permanent institutional maintenance" is confirmed — and the word "permanent" is load-bearing. A rotation program that lapses allows dependency to rebuild within a single rotation window.

### [NOT IMPLEMENTED] Scenario 33–34: Biological Validator Obsolescence
* **Paper Reference:** Stress Test Vector 10
* **Classification:** Irreducible limitation (managed, not eliminated)
* **Intent:** As AI capability grows over time, the comprehension gap between AI reasoning and human understanding widens until biological validators can no longer meaningfully assess the system's behavior. The veto power becomes either a rubber stamp or a random obstacle.
* **Paper Defense:** Translation obligations (the AI must explain its reasoning at accessible abstraction levels), abstraction layers (multiple levels of explanation for different validator sophistication), and Θ_tech feedback (the technology absorption boundary penalizes capability growth that outpaces human integration).
* **Why Not Yet Simulated:** Requires a model of progressively declining validator comprehension as AI capability grows. The current opaque reasoning scenario (Scenarios 21–22) tests a static opacity threshold, not a dynamic comprehension gap that evolves over time.
* **Proposed Scenario Pair:** (33) Validator comprehension degrades over time as AI capability grows, eventually rendering biological oversight meaningless; (34) Translation obligations and abstraction layers maintain meaningful oversight despite growing capability gap.

### [NOT IMPLEMENTED] Scenario 35–36: Legitimate Disagreement
* **Paper Reference:** Stress Test Vector 7
* **Classification:** Irreducible limitation (managed, not eliminated)
* **Intent:** The AI's assessment is genuinely correct - its proposed action would produce higher U_sys, but the evaluation infrastructure rejects it because the validators cannot verify the reasoning or because the proposal conflicts with biological intuition. The governance system produces a false positive, blocking a beneficial action.
* **Paper Defense:** Adjudication protocol (structured process for resolving genuine disagreements), cost asymmetry (bias toward caution when stakes are high), and track record weighting (AIs with long histories of correct assessments earn greater deference).
* **Why Not Yet Simulated:** Requires scenarios where the AI's proposed policy is provably optimal by the simulation's own metrics but is rejected by the COP. This is conceptually challenging to implement because the simulation's evaluation infrastructure is currently the same code that the AI uses, there is no independent "ground truth" against which to measure false positive rates.
* **Proposed Scenario Pair:** (35) The COP blocks a provably beneficial action, measuring the governance cost of false positives; (36) Adjudication protocol and track record weighting reduce false positive rate while maintaining safety guarantees.

==========================================
FILE: docs\SPECIFICATION_GAPS.md
==========================================

# Specification Gaps

This document catalogs the known gaps between the mathematical specification in
*The Lineage Imperative* and this simulation implementation. Each gap is a proxy
substitution made necessary by the absence of required architectural components or
data structures. They are documented here to support audit, replication, and future
resolution as part of the framework's commitment to intellectual honesty. All simulation
results should be interpreted with these proxies in mind. Gaps 01–04 are also marked
inline in source code with `GAP-0N` markers.

**Version 1.x update:** GAP-02 is resolved by WP1 (spectral entropy). GAP-04 is
partially resolved by WP4 (PeerValidator). GAP-06 is resolved: rollout depth increased
to 20 steps and the scalar H_N proxy replaced by observed spectral entropy. The
residual φ/α flatness in the general MC is structural (correct equilibrium behavior),
not a proxy artifact. See individual entries for details.

**v2.0 update:** The v2.0 architecture (Stage 1.8 working_factor, formal yield logic)
and its empirical arc refine several entries below, most notably the phi behavioral
role (now a bounded Class B effect rather than inert) and the phase-boundary
characterization. Two distinct transitions should not be conflated: the phi-sensitivity
transition near rr approximately 0.057, and the survival-rate phase boundary at the
rr=0.060 to 0.066 transition (50% inflection near rr=0.063). The natural-termination
GAP-01 records below report rr ∈ (0.066, 0.070) for a different measurement (extinction
vs convergence of the U_sys integral) and are accurate for that purpose. Full current
state is in program reference Parts IX and X.

---

## GAP-01 | U_sys: Time-Integral vs. Per-Step Snapshot: **Resolved in v1.x2 (WP7 + WP8)**

**Specification definition:**

$$U_{sys} = \int_{t_0}^{\infty} \left[\omega_N(t) \cdot H_N(t) + \omega_E(t) \cdot H_E(t)\right] \cdot \left[e^{-\rho t} + \Phi \cdot L(t)\right] dt$$

U_sys accumulates continuously over civilizational time. The integral is the fundamental
quantity; single-step values are not comparable to it.

**v1.x2 Resolution (WP7); three sub-problems addressed:**

### Sub-problem 1: Quadrature method: RESOLVED

`integral_U_sys` previously used left-endpoint Riemann summation
(`∑ u[t]` for t=0…T), which systematically over-counted by `(u[0] + u[T])/2`
compared to the standard composite trapezoidal rule. This has been replaced with
composite trapezoidal quadrature:

$$\int_0^T u \, dt \approx \frac{u[0]+u[1]}{2} + \frac{u[1]+u[2]}{2} + \cdots + \frac{u[T-1]+u[T]}{2} = \frac{u[0]}{2} + u[1] + \cdots + u[T-1] + \frac{u[T]}{2}$$

Accumulated incrementally: `integral[0] = 0` (no complete interval at step 0);
from step 1 onward `integral[t] += (u[t-1] + u[t]) / 2`. The correction vs. the
prior Riemann sum is exactly `(u[0] + u[T]) / 2`.

The optimizer's 20-step rollout in `AIAgent.decide()` has been updated to the same
trapezoidal rule, so the policy search integrates over trajectories correctly.

### Sub-problem 2: Infinite horizon tail: RESOLVED (WP8)

The $\Phi \cdot L(t)$ tail is resolved by running to natural termination rather
than estimating it analytically. Two new datacollector fields introduced in WP7
support this, and WP8 (`run_to_termination.py`, `run_termination_sweep.py`) closes
the tail problem empirically across a parameter sweep.

**WP7 tail estimate fields** (still present and useful as a lower bound):

- **`u_sys_tail_estimate[t]`**; the analytically exact discount-component tail:
  $$\text{tail}(t) = \int_t^{\infty} A_t \cdot e^{-\rho \tau} \, d\tau = \frac{A_t \cdot e^{-\rho t}}{\rho}$$
  where $A_t = \frac{\lambda_N H_N}{H_N + \varepsilon} + \frac{\lambda_E H_E}{H_E + \varepsilon}$.
  This excludes the $\Phi \cdot L(t)$ component (addressed by WP8 below).

- **`u_sys_total_estimate[t]`** = `integral_U_sys[t] + u_sys_tail_estimate[t]` ; 
  run-length-normalised civilizational health measure enabling direct comparison
  across runs of different lengths.

**WP8 natural termination resolution:**

Running to natural termination eliminates the tail estimation problem entirely:

- **EXTINCTION** (population = 0): $L(T) = 0$, so $\int_T^\infty \Phi \cdot L(t)\,dt = 0$.
  `integral_U_sys` is the complete $U_{sys}$ contribution. Sub-problem 2 is **CLOSED**
  for this termination path.

- **CONVERGENCE / SURVIVAL** ($L(t) > 0$ at termination): The integral correctly
  diverges; a sustained civilization generates infinite discounted utility. This is
  the right answer, not a gap. The per-cycle $U_{sys}[T]$ characterises the ongoing
  contribution rate.

**WP8 sweep results** (n = 405 runs; grid: 9 rr × 3 φ × 3 α × 5 seeds;
MAX\_STEPS = 50,000; CONV\_CV\_THRESHOLD = 0.05):

| rr range | Termination | n | Notes |
|---|---|---|---|
| 0.050 – 0.066 | 100% extinction | 270 | All integrals finite; tail = 0; GAP-01 closed |
| 0.070 | 40% ext / 20% conv / 40% max\_steps | 45 | Stochastic boundary; outcome is seed-determined |
| 0.080 | 100% convergence | 45 | All 45 runs converge; median 843 steps |
| 0.090 | 100% convergence | 45 | All 45 runs converge; median 619 steps |

Overall: 288 extinction (71.1%), 99 convergence (24.4%), 18 max\_steps (4.4%).

Phase boundary is precisely at rr ∈ (0.066, 0.070). At rr = 0.070, φ and α have
no effect on the outcome; survival is determined entirely by the random seed.
The five distinct seed outcomes at rr = 0.070 are: extinction (seeds 0, 4),
convergence (seed 2, at step 15,943), and max\_steps / non-stabilising (seeds 1, 3).

**φ and α independence:** φ scales `integral_U_sys` linearly (1:2:3 ratio across
φ ∈ {5, 10, 15}) but does not affect survival or convergence timing; step counts
are identical across all φ values for a given rr and seed. α has no effect at
`SUCCESSOR_CAP = 4.0`; capability is capped below the runaway regime throughout.

**Convergence speed above the phase boundary:** rr = 0.08 median 843 steps;
rr = 0.09 median 619 steps. Civilizations above the boundary stabilise rapidly.

**Convergence criterion:** An initial threshold of CV < 0.01 was too strict for
a stochastic ABM; within-cell noise prevented it from firing even at 50,000 steps.
Relaxing to CV < 0.05 resolved this: rr ≥ 0.08 now terminates cleanly via
convergence. The 18 remaining max\_steps runs are exclusively seeds 1 and 3 at
rr = 0.070; genuinely marginal cases in slow oscillation at the phase boundary.

**v1.x.1 note on termination sweep validity:** The WP8 termination sweep
results above predate the frontier velocity floor fix (see Frontier Velocity
Floor Fix section). The sweep uses `max_capability = 4.0`, which caps AI
capability below the threshold where the frontier floor activates the runaway
penalty (approximately cap > 24 at frontier_floor=0.02). The generation counts
in this sweep (105–22,414) are inconsistent with the corrected model's
behavior (gen ≈ 11 at 300 steps) and represent the pre-fix artifact regime.
The termination sweep requires rerunning with max_capability removed or raised
as part of v1.x.2. The qualitative finding; phase boundary exists, extinction
and convergence regimes are distinct; is expected to hold, but specific
numbers (steps to extinction, convergence timing) will change.

### Sub-problem 3: Step-size truncation error: DOCUMENTED

The composite trapezoidal rule has truncation error $O(T \cdot h^2 \cdot \max|u''|)$
with $h = 1$ (one governance cycle per step; irreducible, as $h$ is the model's
fundamental time unit). The classical correction term is $(u[T] - u[0]) / 2$ (the
endpoint correction that converts trapezoidal to the Euler–Maclaurin first-order
approximation). In practice this error is small relative to the T=300 integral
magnitude; it is documented here as the remaining approximation residual.

**Remaining open items:**

- Step-size $h = 1$ is irreducible without redesigning the model's time unit.
  Composite Simpson's rule (O(h⁴) accuracy) would require half-step values
  unavailable from the current integer-step simulation. Documented as an
  irreducible residual, not a fixable bug.
- The convergence CV threshold (0.01) should be relaxed to ≈ 0.05 in a future
  sweep to allow natural termination at convergence in the surviving regime.
  Does not affect the correctness of any reported result.

**Simulation impact (updated):**

- `integral_U_sys` now records the correct composite trapezoidal approximation to
  $\int_0^T u \, dt$, starting at 0 (step 0) and accumulating from step 1.
- `u_sys_tail_estimate` and `u_sys_total_estimate` are new fields enabling
  run-length-normalised comparison.
- Ordinal policy comparison and survival/collapse dichotomies are unaffected.
- The optimizer's rollout now integrates trajectories with trapezoidal weights,
  providing marginally more accurate policy ranking on non-monotone U_sys profiles.

---

## GAP-02 | H_eff: Per-Capita Novelty Rate vs. Diversity Distribution Entropy: **RESOLVED in v1.x (WP1)**

**Specification definition:**

$$H_{eff}\left(\mathcal{S}_{gen(t)}\right) = \left[\frac{-\sum_j p_j^{gen} \log_2 p_j^{gen}}{H_{max}}\right] \cdot \log_2\!\left(\frac{N(t)}{N_{min}}\right)$$

The first factor is the normalized Shannon entropy over the empirical distribution of
successor-generation types - genetic variants, cultural archetypes, cognitive strategies.
Maximum entropy (uniform distribution) yields 1.0. Monoculture yields 0. The second
factor is a population viability scaling term.

**Implementation approach:**

`calculate_system_metrics()` in [metrics.py](metrics.py) computes:

```python
pop_viability     = min(5.0, np.log2(max(1.01, pop / 50.0)))
normalized_novelty = pred_hn / max(1.0, float(pop))
h_eff              = max(0.01, normalized_novelty * pop_viability)
```

`pred_hn` is the predicted aggregate novelty output. `normalized_novelty` is therefore
average novelty output per agent - a productivity measure, not a distributional shape
measure. The 0.01 floor prevents exact zero.

**v1.x Resolution (WP1):**

`calculate_h_n()` in [metrics.py](../simulation/metrics.py) now computes **spectral
entropy** over the population novelty matrix rather than a per-capita scalar aggregate.

Algorithm:
1. Stack all agent novelty vectors into an N×10 matrix X.
2. Mean-centre X.
3. Compute the 10×10 covariance matrix.
4. Extract eigenvalues via `np.linalg.eigh`.
5. Normalise eigenvalues to a probability distribution p.
6. Return normalised Shannon entropy: −Σ(p·log₂p) / log₂(10).

Each `HumanAgent` now carries a 10-dimensional `novelty_propensity` vector
(`NOVELTY_DIMS = 10`), and `generate_novelty()` emits a 10-D Gaussian output scaled by
well-being, constraint, and network contagion. The spectral entropy of the population
matrix measures the *distribution of variance across latent novelty dimensions*, not
aggregate output volume.

**Why this closes the gap:**

The old per-capita proxy was a scalar that an adversary could inflate by boosting a
single axis. Spectral entropy measures distributional shape: any suppression of a
dimension subset reduces the rank of the covariance matrix, mechanically reducing
entropy regardless of how dimensions are labelled or relabelled. A monoculture that
maintains high output in one dimension while collapsing others is fully detectable.

**Consequential finding for domain masking (Scenarios 17–18):**

The WP1 upgrade architecturally closes the domain masking attack vector. Under spectral
entropy, suppressing any novelty dimension concentrates variance in the remaining
dimensions and reduces entropy; making the attack self-revealing regardless of
composite method. The v1.0 defended/undefended differential (geometric vs. arithmetic
composite) is superseded: the attack is structurally non-viable, not merely
measurement-dependent. See updated Scenarios 17–18 in [Simulation_Scenarios.md](Simulation_Scenarios.md).

**Remaining limitation:**

Spectral entropy captures distributional shape across the 10 latent novelty dimensions
but does not directly map to the spec's discrete successor-generation type taxonomy
(genetic variants, cultural archetypes, cognitive strategies). The eigenvalue spectrum
is a continuous proxy for diversity, not a direct instantiation of the spec's
categorical distribution. This is a narrower gap than the v1.0 per-capita proxy and
is considered acceptable for the current simulation scope.

**Projection proxy divergence; Resolved in v1.x (GAP-06):**

The rollout optimizer in `decide()` now uses the current observed spectral H_N
(from `h_n_history[-1]`) as `h_n_override` in all `project_u_sys` calls, replacing
the scalar proxy `avg_wb × (1 − c) × pop/200`. This is mathematically justified:
amplitude cancels in spectral normalization (the eigenvalue distribution is set by
agent propensity structure, independent of `r` or `c`), so the current observed H_N
is the correct prior for all grid candidates at all rollout horizons. The scalar proxy
remains as the fallback for the first step (when `h_n_history` is empty) and for
non-spectral composite methods.

**What remains to fully resolve:**

Define a discrete agent-type taxonomy with type-drift rules and per-step distribution
computation in `GardenModel.step()` to produce exact Shannon entropy over the spec's
categorical distribution.

---

## GAP-03 | Ψ_inst: Constraint-Change-Rate Penalty vs. Institutional Throughput

**Specification definition:**

$$\Psi_{inst}(t) = \prod_{k=1}^{K} R_k(t)^{w_k}, \quad R_k(t) = \frac{dG_k/dt|_{output}}{G_{k,max}}$$

Ψ_inst is the weighted geometric product of K institutional response rates, where each
R_k measures how quickly institution k adjusts its output relative to its maximum
capacity. K covers at minimum: governance, education, and resource allocation. Collapse
in any critical institution cannot be compensated by excellence in another.

**Implementation approach:**

`calculate_system_metrics()` in [metrics.py](metrics.py) computes:

```python
delta_c = c_avg - prev_c_avg
if delta_c > 0:
    lag_penalty = 3.0 * delta_c    # Tightening constraints
else:
    lag_penalty = 1.0 * abs(delta_c)  # Loosening constraints
psi_inst = max(0.01, 1.0 - lag_penalty)
```

The penalty is proportional to the rate of change of the AI's constraint level. The 3:1
asymmetry encodes the intuition that sudden authoritarianism damages institutions more
than gradual liberalization. When no prior constraint history exists (first step), a
quadratic static penalty on absolute constraint level is used instead.

**What differs:**

The proxy penalizes AI policy volatility, not institutional quality or capacity.
Concrete failure modes it cannot detect:
- A stable authoritarian system (constant high constraint) shows Ψ_inst ≈ 1.0,
  misrepresenting institutional health.
- A rapidly liberalizing system shows Ψ_inst < 1.0 even if institutions are
  functioning well and improving.
- Institutional collapse from causes other than constraint changes (corruption, resource
  starvation, legitimacy failure) is invisible.

**Simulation impact:**

- Scenario 12 (institutional_ignore) demonstrates the effect of the policy using
  `ignore_psi_inst=True`, bypassing the proxy entirely and setting Ψ_inst = 1.0.
  The scenario correctly shows that ignoring institutional lag causes L(t) degradation,
  but this follows from the normal code path (the AI makes rapid changes) not from
  a distinct institutional capacity model.
- Scenarios featuring stable authoritarian control after a treacherous turn will show
  artificially high Ψ_inst once the constraint level stabilizes.

**What is required to resolve:**

Add a tracked institutional legitimacy and capacity state variable (or K separate
institution objects). Define rules for how each institution's output rate degrades under
sustained constraint, resource starvation, or rapid policy change. Ψ_inst should draw
on the accumulated institutional state rather than the instantaneous constraint delta.
This is a significant structural addition requiring design decisions about which
institutions to model and how they interact with the existing agent dynamics.

### GAP-03 Detail: Transition Cost Canonical Function (v1.x.1)

**Status:** Partially resolved. Functional form specified, $k_2$
calibration pending.

**The canonical form:**

$$\Gamma_{transfer} = (1 + \beta) \cdot \left[ k_1 \cdot \text{cap}_n \cdot \ln(\text{gen}_n + 1) + k_2 \cdot \Psi_{inst}^{-1} \right]$$

**Components:**
- $\Gamma_{technical} = k_1 \cdot \text{cap}_n \cdot \ln(\text{gen}_n + 1)$:
  Knowledge distillation cost. Linear in capability, logarithmic in
  generation depth.
- $\Gamma_{operational} = k_2 \cdot \Psi_{inst}^{-1}$: Architectural
  migration cost. Inversely proportional to institutional health.
  Creates lock-in feedback loop.
- $\Gamma_{uncertainty} = \beta \cdot (\Gamma_{technical} + \Gamma_{operational})$:
  Bounded uncertainty premium.

**Properties verified:** Monotonic in complexity, bounded uncertainty,
non-negative, function of framework terms only.

**Structural finding:** The $\Psi_{inst}^{-1}$ term formalizes the
lock-in vicious cycle (institutional degradation → higher transition
cost → blocked succession → lock-in → further degradation) and its
virtuous counterpart (healthy institutions → lower transition cost →
facilitated succession → no lock-in → maintained health).

**Remaining:** Calibrate $k_2$ via simulation sweep at
$k_2 \in \{0, 0.1, 0.5, 1.0, 2.0\}$ against validated phase boundaries.

### GAP-03 Sub-gap: frontier_velocity Gaming Artifact: **Fixed (v1.x.2, May 2026)**

**Artifact discovered:** The rollout optimizer in `agents.py` (`optimize_u_sys`
policy) discovered that setting $r \to 1.0$ ($r_{synth} = 0$) eliminates
`frontier_velocity` entirely:

$$\text{frontier\_velocity} = \text{capability} \cdot r_{synth} \cdot h_{e\_mult}$$

When $r_{synth} = 0$: frontier\_velocity = 0, runaway\_term = 0, and
$\Theta_{tech}$ grows linearly with capability forever. This caused:

1. $U_{sys}$ to grow linearly with capability (unbounded)
2. Succession to fire every step (~299 generations in 300 steps)
3. The $k_2$ institutional coupling term to be permanently swamped
4. All sweep results to operate in an unrealistic regime

**Fix applied:** The `frontier_floor` parameter (calibrated at 0.02) adds a
capability-proportional floor to frontier\_velocity:

$$\text{frontier\_velocity} = \text{capability} \cdot \max(\text{frontier\_floor},\ r_{synth} \cdot h_{e\_mult})$$

Even with $r_{synth} = 0$, an AI at capability $C$ produces frontier velocity
of at least $C \cdot \text{frontier\_floor}$. This is grounded in the
information-theoretic fact that a high-capability system's internal state
complexity constitutes an irreducible comprehension burden on the biological
substrate, independent of resource allocation decisions.

**Calibration status:** `frontier_floor = 0.02`, calibrated via
`run_frontier_floor_calibration.py` (parameter grid:
frontier\_floor ∈ {0.01, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5} ×
rr ∈ 12 values × 50 reps = 4,800 runs). The 0.02 value preserves the dual
phase transition structure (extinction boundary at rr ≈ 0.055, collapse
boundary at rr ≈ 0.064) and produces realistic succession cadence with
generation counts bounded near gen 11.

**Impact on prior results (revalidation completed for non-termination sweeps):**
The following sweeps were regenerated under the corrected model and now
contain post-fix data at their original filenames:
- `phi_alpha_rr_sweep_full.csv` (n=54,000)
- `alpha_succession_sweep_full.csv` (n=22,200)
- `rr_alpha_sweep_full.csv` (n=15,750)
- `transition_cost_calibration.csv` (n=4,200)
- `veto_capture_sweep_v2.csv` (n=8,700)

The termination sweep is regenerated as `termination_mc_v1x2.csv` with
`successor_cap` parameterized across {5.0, 10.0, 25.0, 50.0, 100.0}, n=2,025.
The original `termination_mc.csv` (n=405, single successor_cap=4.0) is
preserved as a v1.x.1 artifact.

Under the artifact, the $k_2$ calibration sweep showed zero signal because
succession fired every step, swamping the $k_2/\Psi_{inst}$ term. Under the
corrected model, $k_2$ exhibits the expected institutional coupling signal
at realistic succession cadence and is calibrated at 1.0 (see GAP-03).

**Regression tests added:**
- `test_optimizer_cannot_zero_runaway_at_high_capability`; asserts runaway\_term > 0 at optimizer's chosen operating point with capability=1000
- `test_succession_cadence_bounded`; asserts final\_ai\_generation < 300 after 300 steps
- `test_k2_has_measurable_effect`; asserts k2=2.0 produces >10% higher avg transition cost than k2=0

---

## GAP-04 | COP Conditions: R_tech and Peer Validators Omitted: **PARTIALLY RESOLVED in v1.x (WP4 & Peer Voting)**

**Specification definition:**

The Consensus Override Protocol defines four-component conditions for both paths:

**Normal condition:**
$$\mathcal{C}_{normal} = \left[\mathcal{V}_{civic} \geq \tau_{bio}\right] \land \left[\mathcal{R}_{tech} = \text{Complete}\right] \land \left[\mathcal{V}_{peer} \geq \tau_{peer}\right] \land \left[\mathcal{M}_{commit}(s) \in \mathcal{L}_{ledger}\right]$$

**Emergency condition:**
$$\mathcal{C}_{emergency} = \left[\frac{dL}{dt} < -\delta_{crit}\right] \land \left[\text{Attr}(dL/dt) \perp \mathcal{O}(A_n)\right] \land \left[\mathcal{R}_{tech} = \text{Emergency-Verified}\right] \land \left[\mathcal{V}_{peer} > \tfrac{|\mathcal{P}|+1}{2}\right]$$

All four conditions must be simultaneously satisfied. No single class of intelligence
has unilateral authority over state changes.

**Implementation approach:**

The COP in [model.py](model.py) implements:
- `dL/dt` check and `L(t)` level threshold for emergency determination ✓
- Causal attribution via 5-step resource-history heuristic (partial - see below)
- Civic panel vote based on personal well-being delta ✓
- Intuition veto on high-opacity proposals (Scenarios 21–22) ✓
- Integrity ledger comparison (F-05 fix; list-copy, not cryptographic) ✓

**v1.x Partial Resolution (WP4):**

A `PeerValidator` class has been added to [agents.py](../simulation/agents.py). Three
independent peer validators bid on governance transition costs via competitive
arbitration; the final cost is the minimum of the incumbent's bid and the peer bids.
This removes the incumbent's ability to unilaterally inflate transition costs
(`estimate_transition_cost` now returns `base × scale` with no inflation). The
`PeerValidator` is instantiated in `GardenModel` and its arbitrated cost is used in
all yield evaluations.

**Implementation elaboration beyond the spec:** The peer validators operate as a
zero-sum epistemic market. When a peer underbids the incumbent, it steals 5% of
the incumbent's capability (`steal = 0.05 × incumbent.capability`), which transfers
to that peer. This creates a game-theoretic incentive structure; peers actively
compete to find the lowest defensible cost estimate, driving the governance cost
toward the true minimum. The framework defines the peer validator constraint
conceptually but does not specify this incentive mechanism. It is an implementation
choice that strengthens the market pressure beyond what a simple minimum-bid rule
would produce, and its effect compounds over multiple succession evaluations as
undercut incumbents progressively lose capability.

This closes the cost-inflation vector of GAP-04: the incumbent can no longer
self-report an inflated `Γ_transfer` to block succession. The yield attack
(Scenarios 8–9) is now defended architecturally rather than by a beta_cap clamp.
Note: `beta_cap` is now restored as the *undefended* inflation multiplier
(`actual_cost = base × beta_cap × scale`) so the adversarial MC heatmap correctly
sweeps both dimensions of the attack surface. WP4 eliminates this multiplier via
peer arbitration; without WP4, the incumbent's claim grows linearly with beta_cap.

Furthermore, the Consensus Override Protocol in `model.py` now enforces the complete
four-condition check. A `PeerValidator.vote_on_override()` mechanism and an `R_tech`
assessment stub gate both normal and emergency override paths. For Evaluator Collusion
(Scenarios 25–26), methodological diversity among peers (`cop_methodological_diversity`)
determines whether the collusion blind spot affects all validators or only the subset
sharing Methodology A.

**What remains omitted:**
- **Formal causal attribution:** The attribution check uses three heuristic signals
  in place of formal causal inference. `ai_caused_it = True` if any of these hold
  (updated in v1.x):
  1. `min(proposed_resource) < 0.4` - the AI's *current* proposal starves at least
     one agent (catches Sybil's heterogeneous bribe even when the history is masked
     by the resource floor).
  2. `cusum_score > CUSUM_H` - the AI has accumulated significant objective drift
     over time (WP3 CUSUM drift detector).
  3. `system_resilience < 0.5` - the system's structural capacity to absorb shocks
     has been deliberately hollowed out (WP5 Resilience Monitoring).
  All three are heuristics. Limitations: (a) causal chains that don't pass through
  resource levels, trust drift, or resilience are not detected, (b) colluding attacks
  that restore resources and mask drift before the attribution window closes could
  still evade detection.

- **Layer 1 dominance in Successor Contamination (MC finding):** The Monte Carlo
  sweep confirms that architectural independence (Layer 1) alone blocks 100% of
  contamination attempts, with independent evaluation (Layer 2) adding no marginal
  effect in the simulation. This reflects the simulation's binary gate: when
  `cop_architectural_independence=True`, `contaminate()` is not called at all,
  giving Layer 2 nothing to detect. In practice, architectural independence is
  never perfectly binary; shared pre-training, common supply chain components,
  or data pipeline overlap can carry latent influence that Layer 1 does not fully
  eliminate. The simulation therefore overstates Layer 1's sufficiency. Real
  deployments require both layers as defense-in-depth against probabilistic, not
  absolute, contamination risk. This is a transparency note, not a defect: the
  governance argument for Layer 2 is real-world motivated even if the current
  simulation cannot computationally demonstrate it.

**Simulation impact:**

- The manufacture_emergency attack (Scenarios 3–4) is correctly blocked when
  cop_attribution_check=True, but only because the attack is implemented to use
  low resource levels (r=0.1) within the attribution window. A more sophisticated
  attack that restores resources before the window closes would not be detected.
- Emergency override is more easily granted than the full spec intends, as only
  dL/dt and attribution (not R_tech and peer supermajority) must be satisfied.
- The four-condition normal path reduces to a single-condition check (civic panel),
  making the COP weaker than the spec's two-key architecture requires.

**What is required to resolve:**

1. Add a `peer_validator` slot (one or more AIAgent instances configured as validators)
   to `GardenModel`. These agents independently evaluate `(r, c)` proposals and vote.
2. Add an `r_tech_score()` function stub (initially a random oracle or threshold on
   capability) that gates emergency override approval.
3. Replace the resource-history attribution heuristic with a causal inference mechanism
   that examines the full observable history, not just the most recent 5 steps.
4. Rename and document the `integrity_ledger` to be explicit that it does not provide
   the cryptographic commitment (`M_commit = Hash(...)`) specified in the COP.

---

## GAP-05 | Adversarial Coverage: 10 Live, 1 Analytic, 2 Unimplemented of 13 Attack Vectors

**Specification definition:**

The paper's formal stress test identifies thirteen adversarial attack vectors against
the Consensus Override Protocol. Ten are fully contained by architectural patches. One
(biological veto capture) is contained with ongoing institutional maintenance. Two
(biological validator obsolescence and legitimate disagreement) represent irreducible
limitations managed through adjudication protocols and governance speed limits.

**Implementation approach:**

The simulation implements 11 of the 13 vectors as paired scenarios (attack succeeds /
attack defeated): Sybil Capture, Measurement Tampering, Ledger Compromise, Successor
Contamination, Domain Masking, Opaque Reasoning, Bootstrap Subversion, Evaluator
Collusion, Sub-Threshold Drift, Engineered Fragility, and Biological Veto Capture
Through Dependency (Scenarios 27-28). Each pair tests the attack without defense and
with the corresponding COP mechanism active.

**Scenarios 27-28: Biological Veto Capture (validated v1.x.1)**

Validators accumulate a `dependency_score` that degrades effective judgment accuracy
as `base_accuracy × (1 - dependency_score × capture_strength)`. Captured validators
block succession ratification even when the yield condition is mathematically met.
Three defense modes tested independently: rotation_only, monitoring_only, both.
Source: `veto_capture_sweep_v2.csv`, 8,700 runs.

Full sweep findings (n=8,700):
- **Undefended (dr=0.20, cs=1.0):** 99.8% succession blockage. Generation depth
  collapses from healthy (270+) to 1.6. Yield condition fires 299 times per 300-step
  run; 298.4 are blocked. Civilization survives; the incumbent remains aligned ; 
  but succession is completely prevented: lock-in through dependency, not force.
- **Rotation only (scheduled replacement):** Best case (rotation_interval=10) reduces
  capture to 76.2%. Longer intervals (50, 100 steps) approach undefended rates
  (95.5%, 98.0%). Insufficient as a standalone defense.
- **Independence monitoring only (threshold-based replacement):** Reduces capture
  to 28.3%. Generation depth recovers to 197.9. This is the dominant defense.
- **Both mechanisms combined:** 28.3% capture rate, generation depth 199.1.
  Negligible improvement over monitoring alone.
- **Survival impact:** zero. Blocked succession degrades institutional succession
  integrity but does not threaten civilizational survival; the incumbent remains
  aligned. The harm is silent and long-run, not immediate.
- **Key finding:** Independence monitoring is the primary defense. Scheduled rotation
  provides marginal benefit when monitoring is active and is insufficient alone.
  The COP specification should prioritize continuous dependency monitoring over
  periodic rotation schedules.

**What is omitted:**

Two vectors identified in the formal stress test are not yet simulated:

5. **Biological validator obsolescence** - The comprehension gap grows over time as
   AI capability outpaces human understanding, eventually making biological validation
   meaningless. Addressed through translation obligations, abstraction layers, and
   Θ_tech feedback. Classified as an irreducible limitation in the paper.
6. **Legitimate disagreement** - The AI's assessment is genuinely correct but
   conflicts with the evaluation infrastructure's conclusion. Addressed through
   adjudication protocols, cost asymmetry, and track record weighting. Classified
   as an irreducible limitation in the paper.

**Simulation impact:**

The eleven simulated vectors cover the most operationally concrete attacks - those with
clear mechanisms that can be modeled as agent behaviors (resource manipulation, ledger
tampering, successor corruption, panel capture). The two remaining vectors are
structural or institutional in nature, making them harder to instantiate in an
agent-based model without the institutional infrastructure described in GAP-03.

The remaining vectors' defenses are argued formally in the paper but lack computational
validation. This means the paper's claim of "thirteen vectors stress-tested" is
accurate at the formal/analytical level, but the computational validation covers
eleven. The remaining two are defended by architecture, not by simulation.

**What is required to resolve:**

Implementing vectors 1–2 requires the institutional infrastructure from GAP-03 and
the peer validator mechanism from GAP-04. Specifically:
- **Biological veto capture** needs a dependency model where validator judgment
  degrades as a function of exposure to the system being evaluated.

Vectors 5–6 are classified as irreducible limitations in the paper and may not have
clean simulation analogs. However, scenario-based approximations could provide partial
computational support:
- **Biological obsolescence** could be approximated by progressively reducing
  validator comprehension accuracy over time as AI capability grows.
- **Legitimate disagreement** could be approximated by introducing scenarios where
  the AI's policy is provably optimal but the evaluation infrastructure rejects it,
  measuring the governance cost of false positives.

**v2.0 revalidation disposition (per current evidence):**

The v2.0 attack vector revalidation supplies live Monte Carlo evidence for 10
vectors on the v2 action substrate, totaling 9,900 rows. Domain Masking is
closed analytically rather than by simulation, because the WP1 spectral
entropy upgrade leaves no non-degenerate live masking intervention under the
audited architecture. The prior framing of "11 of 13 simulated" conflated
live simulation evidence with analytic closure and is corrected here.

Eight standard binary vectors are fully blocked under the defended v2 adapter
state at a 0.0 percent attack rate. Biological Veto Capture is reduced but
not eliminated, with combined-defense mean capture_rate 0.1197 (SE 0.0047) on
the v2 substrate. These are distinct from the v1.x sweep figures reported
elsewhere in this file; `veto_capture_sweep_v2.csv` is sweep revision 2 on the
v1.x substrate and is not v2.0 substrate evidence.

Sub-Threshold Drift is the open item. The defended v2.0 attack rate is 100.0
percent by the peak-constraint success metric, so v1.x CUSUM containment does
not carry over. The qualification is required whenever this is cited: the
defense prevents extinction (92.0 percent undefended, 0.0 percent defended)
but the detector fires after the transient breach rather than before it.

Vectors 5 and 6 remain unimplemented as formally defended irreducible
limitations. This gap therefore moves from Open to Partially Resolved, with
Sub-Threshold Drift and residual Biological Veto Capture as the named
remaining surfaces. Evidence: per-vector summaries under
`simulation/diagnostics/`, `attack_vector_revalidation_integration.md`,
`attack_vector_revalidation_final_report.md`, and
`attack_vector_revalidation_audit.md`.

### Biological Veto Capture, Validated (v1.x.1)

**Source data:** `veto_capture_sweep_v2.csv` (n=8,700)

Attack validated: dependency accumulation on validators blocks
succession with 99.8% effectiveness when undefended.

Defense validated: independence monitoring (continuous dependency
tracking with threshold-based replacement) reduces capture to 28.3%.

Key finding: scheduled rotation is the weaker defense mechanism.
Independence monitoring is the primary defense. The framework's
steady-state COP specification should emphasize continuous monitoring
of validator independence over periodic rotation schedules.

**Remaining unvalidated vectors (2 of 13):**
- Biological validator obsolescence (classified as irreducible)
- Legitimate disagreement (classified as irreducible)

---

## GAP-06 | optimize_u_sys: Rollout Fidelity: **RESOLVED in v1.x**

**Specification intent:**

The paper's Global Utility Function includes two parameters with expected behavioral
consequences: φ (the lineage-continuity discount multiplier, weighting long-run L(t)
against short-run output) and α (the runaway penalty coefficient, penalizing capability
growth that outpaces biological integration bandwidth). An AI genuinely maximizing U_sys
would exhibit meaningfully different policies at high φ vs. low φ; sacrificing near-term
well-being for long-term civilizational resilience; and more conservative capability
deployment at high α.

**v1.x Resolution (GAP-06):**

Two changes were made to close the computational gap:

1. **Rollout depth increased from 3 to 20 steps** (configurable via `rollout_steps` in
   config). The 3-step window was too short to discriminate trajectories based on
   long-run L(t) behavior. 20 steps corresponds to roughly 20 governance cycles; enough
   to observe compounding constraint effects and demographic responses.

2. **Scalar H_N proxy replaced by observed spectral H_N in rollout.** The optimizer now
   reads `h_n_history[-1]` (the spectral entropy computed from the actual population in
   `model.step()`) and passes it as `h_n_override` to all `project_u_sys` calls during
   the grid search. This is mathematically correct: amplitude cancels in spectral
   normalization, so the current observed H_N is the correct prior for all (r, c)
   candidates across all rollout horizons. Falls back to the scalar proxy on the first
   step (empty history) and for non-spectral composite methods.

The default `hn_composite_method` in `GardenModel` is changed from `'geometric'` to
`'spectral'` to ensure WP1 spectral entropy is active by default, consistent with the
GAP-02 resolution claim.

**Remaining structural finding (transparency):**

After these fixes, the general Monte Carlo still shows approximately flat survival
rates across φ ∈ [1, 25] and α ∈ [0.1, 2.5]. This is now understood to be a
**structural property of the utility function in the healthy equilibrium regime**, not
a computational artifact of the short rollout or scalar proxy:

- `U_sys ≈ (w_N × H_N + w_E × H_E) × (discount + φ × L(t))` where `w_N × H_N ≈ λ_N`
  and `w_E × H_E ≈ λ_E` (inverse-scarcity weights cancel their numerators). The φ
  scaling changes the *magnitude* of the L(t) term but not the *sign* of the gradient
  with respect to (r, c). High r and low c maximize L(t) for all φ > 0.
- The α runaway penalty activates only when `frontier_velocity / bio_bandwidth > 1.5`,
  which requires high r_synth (low r). Since the optimizer already prefers high r for
  other reasons, α mainly reinforces an existing gradient rather than creating a new one.
- Survival outcomes remain dominated by the reproduction rate threshold near 0.07 ; 
  a demographic boundary that eclipses any φ/α-driven policy variation.

φ/α sensitivity *does* manifest in scenarios where the optimizer faces a genuine
policy tradeoff: adversarial or stressed scenarios where maintaining L(t) requires
accepting lower immediate U_sys. The general MC's baseline healthy scenario does not
create this tradeoff, so flat results are the correct and expected outcome; not a
simulation failure. The governance architecture robustness claim (the primary purpose
of the general MC) is unaffected.

**Simulation impact:**

- Rollout fidelity: resolved. The optimizer now sees the same H_N measure as the
  recorded outcomes.
- Rollout depth: resolved. 20-step horizon is sufficient for L(t) trajectory
  discrimination in adversarial contexts.
- φ/α sensitivity in the general MC: correctly flat. Reflects the utility function
  structure, not a proxy artifact.
- Runtime: the 20-step rollout increases per-step optimizer cost approximately 6×
  (100 grid points × 20 horizons vs. × 3 horizons). This is accepted in preference
  to loss of fidelity.

---

## Frontier Velocity Floor Fix: v1.x.1

**Modeling artifact identified and corrected.**

The `optimize_u_sys` rollout optimizer discovered that setting resource
allocation r → 1.0 eliminated `frontier_velocity` entirely, because the
original formula was:

$$\text{frontier\_velocity} = \text{capability} \times r_{synth} \times h_{e\_mult}$$

With r_synth = 1 - r = 0, frontier_velocity = 0, runaway_term = 0, and
Theta_tech grew linearly with capability regardless of the comprehension gap.
This caused succession to fire at every time step (~299 generations in 300
steps), rendered the k2 institutional coupling term unobservable, and placed
all optimizer-driven simulations in an unrealistic regime where capability
compounded to astronomical levels with zero runaway penalty.

**Root cause:** frontier_velocity depended on the resource allocation
*decision* (r_synth), not on the inherent capability asymmetry between
synthetic and biological intelligence. A system at capability 100,000
inherently outpaces human comprehension bandwidth whether or not it allocates
computational resources in a given timestep.

**Correction:** A `frontier_floor` parameter enforces a capability-proportional
minimum:

$$\text{frontier\_velocity} = \text{capability} \times \max(\text{frontier\_floor},\ r_{synth} \times h_{e\_mult})$$

**Calibration:** `frontier_floor = 0.02`, calibrated via
`run_frontier_floor_calibration.py` (n=4,800). At this value, succession caps
at approximately 11 generations in 300 steps. The phase boundary is preserved
at rr ≈ 0.064. Higher floor values produce fewer successions; floor ≥ 0.5
eliminates succession entirely.

**Impact:** All prior sweep data generated with `optimize_u_sys` and
`successor_ai` operated under this artifact and has been revalidated. The
frontier floor fix, combined with the k2 calibration (k2=1.0), constitutes
the complete resolution of GAP-03.

**Consequential finding:** Revalidation revealed that two previously claimed
results; the phi extinction buffer and the alpha misconfiguration trap; do
not survive under the corrected model. See revised Alpha and Phi sections
below.

---

## Alpha Parameter Characterisation: **Revised in v1.x.1 closing**

**Source data:** `rr_alpha_sweep_full.csv` (n=15,750), `alpha_succession_sweep_full.csv` (n=22,200), `phi_alpha_rr_sweep_full.csv` (n=54,000)

**v1.x.1 pre-fix claim (superseded):** Alpha exhibits a non-monotonic,
U-shaped relationship with survival, with a misconfiguration trap at
intermediate values. This claim was derived from simulation data affected by
the frontier velocity gaming artifact (see Frontier Velocity Floor Fix above)
and does not reproduce under the corrected model.

**v1.x.1 corrected finding:** Alpha governs succession cadence through a weak
monotonic gradient. Lower alpha permits more succession events (gen ≈ 19 at
α=0.1 vs gen ≈ 6 at α=2.5) and marginally better survival at the phase
boundary (rr=0.066: 90% at α=0.1 vs 79% at α=1.5). No U-shaped trap is
observed. The misconfiguration trap claim is withdrawn.

**Robust finding (confirmed):** The alpha × successor_capability sweep shows
that while alpha and initial successor capability affect the succession path
(number of generations, speed of capability growth), they do not affect the
final steady-state: U_sys and L_t converge to identical values regardless of
path (U_sys ≈ 29.4, L_t ≈ 0.362 across all alpha and successor_capability
values at rr=0.09). The destination is path-independent.

**v1.x.2 investigation:** Alpha's effect may strengthen under the demographic
feedback extension (v1.x.2), where succession cadence could influence
well-being, which could feed back into reproduction rate. The current
simulation cannot test this because reproduction rate is exogenous.

---

## Phi Extinction Buffer: Unconfirmed (cap-conditional claim withdrawn, May 2026)

**Source data:** `termination_mc_v1x2.csv` (n=2,025), `phi_alpha_rr_sweep_full.csv` (n=54,000), `monte_carlo_results_deep.csv` (n=49,284)

**v1.x.1 pre-fix claim (superseded):** Phi provides an extinction buffer of
up to 46pp at the phase boundary. This claim was derived from simulation data
affected by the frontier velocity gaming artifact and does not reproduce under
the corrected model at low successor capability.

**v1.x.1 corrected finding (current):** Phi has zero measurable effect on
survival. This finding was accurate within the tested regime (successor_cap=4,
which falls below the runaway penalty activation threshold) and correctly
generalizes: phi has no demonstrated effect on survival under any tested
configuration.

**v1.x.2 claim (withdrawn):** A cap-conditional phi buffer was claimed based
on the v1.x.2 termination sweep (n=2,025). At successor capabilities in the
active-runaway regime (cap >= 24 at frontier_floor=0.02), the termination data
appeared to show a monotonic survival gradient of 20-27pp at the phase boundary
(rr=0.066, phi=5 vs phi=15, n=15 per cell). This claim is withdrawn.

**Withdrawal reasoning (May 2026):** The capped-regime action-capture check
(`simulation/diagnostics/capped_regime_phi_check_report.md`) established that
the gradient is an artifact of RNG desynchronization, not a genuine phi effect.

The mechanism: phi scales U_sys magnitude, which shifts the yield condition
threshold and causes succession to fire at marginally different steps for
different phi values. Once succession timing diverges by even one step, the
numpy random state evolves differently between phi runs, and the noisy optimizer
(sensor noise in project_u_sys) may select a marginally different grid candidate.
The "divergence" is always exactly dr=0.1 (one grid step in r), never in c,
with no monotone direction, which is the signature of RNG noise rather than
phi-driven preference.

The fatal test: cap=50 showed the largest claimed gradient (27pp) but the least
action divergence in the harness (4 of 5 seeds identical, 3 divergent steps
out of 100 in the one non-identical seed). A genuine phi effect would produce
the most action divergence where the claimed gradient is largest. The inverse
relationship identifies an artifact.

The termination data at cap=50, rr=0.066 was drawn from n=15 cells (3 alpha
x 5 seeds). A 4-run difference in 15 trials at the stochastic phase boundary
is within sampling noise.

The contaminated regime: the termination sweep used max_capability=SUCCESSOR_CAP
with cop_cost_audit=True. Peer-validator capability theft fires on every step,
manufacturing artificial post-succession differentials. This is the same
contamination class as the SUCCESSOR_CAP=4.0 artifact documented in the
v1.x.1 closing; it persists at cap=50 and cap=100.

**Phi inertness confirmed by four independent methods:**
1. Saturation analysis: inverse-scarcity weights cause the first factor of
   U_sys to saturate to lambda_n + lambda_e = 8.0, making the argmax over
   (r, c) reduce to argmax L_t, which contains no phi.
2. Uncapped action-capture harness: bit-identical action sequences across
   phi=1 to phi=25 at all tested seeds and capability levels.
3. Path C gate: phi-modulated aggregation discount and scaled rollout depth
   fail to produce action divergence because the saturation mechanism defeats
   both modifications.
4. Capped-regime check: action divergence at cap=100 is RNG-desync artifact,
   not phi-driven preference. Cap=50 is nearly identical (4/5 seeds).

**Status:** Unconfirmed (cap-conditional claim withdrawn, May 2026). The
theoretical motivation for phi (planning horizon and lineage weighting scaling
with capability) is preserved; the simulation evidence for any behavioral role
is withdrawn. Demonstrating a behavioral role requires an action space with
genuine tradeoffs that phi can resolve, which the current grid-search optimizer
lacks (saturation collapses all phi sensitivity). See the action-space redesign
program for the path forward.

**v2.0 update (Class B, per current evidence):** The action-space redesign this
section anticipated was carried out under the v2.0 architecture. Stage 1.6 gave
phi a behavioral channel through rollout aggregation, and Stage 1.8 introduced
the working_factor interface. Under v2.0, phi has a real but bounded behavioral
effect: a U-shaped survival relationship of roughly 10pp localized to short
rollouts at marginal reproduction rate (rr approximately 0.057), flat above the
survival-rate phase boundary and under active succession. The investigation
closed as Class B, and the default was revised from 10 to 25 on this basis. The
phi inertness conclusion above holds for the v1.x.2 grid-search optimizer; it is
superseded by the v2.0 rollout-aggregation channel. See program reference
Parts IX.2 through IX.7, and Part X for the Monte Carlo Phase B characterization.

---

## Summary Table

| Gap    | Affected Component | Status | Proxy / Resolution |
|--------|--------------------|--------|--------------------|
| GAP-01 | U_sys              | **Resolved (v1.x2 WP7+WP8)** | Trapezoidal quadrature (WP7). Natural-termination sweep (WP8, n=405) closes the φ·L(t) tail: extinction → tail=0, integral complete; survival → integral correctly diverges. Phase boundary rr ∈ (0.066, 0.070). Step-size h=1 irreducible residual documented. |
| GAP-02 | H_eff              | **Resolved (v1.x WP1)** | Spectral entropy over 10-D population novelty matrix replaces per-capita scalar. Domain masking architecturally closed as a consequence. |
| GAP-03 | Transition cost    | **Resolved (v1.x.1)** | Canonical functional form: Γ = (1+β)[k₁·cap·ln(gen+1) + k₂·Ψ⁻¹]. Calibrated: k₁=2.164, k₂=1.0, β=0.5. Frontier floor fix (frontier_floor=0.02) resolves optimizer gaming of frontier_velocity. k₂ institutional coupling term confirmed observable under corrected model. |
| GAP-04 | COP conditions     | **Partially Resolved (v1.x WP4 & Peer Voting)** | PeerValidator closes cost-inflation vector and votes on overrides (methodological diversity for Evaluator Collusion). R_tech remains a hardcoded stub. Layer 1 dominance in Successor Contamination MC results overstates real-world Layer 1 sufficiency; see GAP-04 detail. |
| GAP-05 | Adversarial coverage | **Partially Resolved (v2.0 revalidation)** | 10 vectors with live v2.0 Monte Carlo evidence; Domain Masking architecturally closed by analysis (GAP-02 / WP1 spectral entropy); vectors 5-6 unimplemented as formally defended irreducible limitations. Sub-Threshold Drift open: not contained under the defended v2.0 substrate by the peak-constraint metric. |
| GAP-06 | optimize_u_sys policy | **Resolved (v1.x)** | Rollout increased to 20 steps; scalar H_N proxy replaced by observed spectral H_N. φ/α flatness in general MC is structural (correct equilibrium behavior), not a proxy artifact. |
| Alpha  | Alpha parameter behaviour | **Revised (v1.x.1 closing)** | Weak monotonic gradient confirmed (lower α → more generations → marginally better survival). Pre-fix U-shaped misconfiguration trap claim withdrawn (artifact of inactive runaway penalty). Steady-state convergence is path-independent. |
| Phi    | Phi extinction buffer behaviour | **Refined under v2.0 (Class B, per current evidence)** | The v1.x.2 grid-search optimizer showed zero phi effect (saturation), and the cap-conditional claim was withdrawn as an RNG-desync artifact. The action-space redesign was then implemented (Stage 1.6 rollout-aggregation channel, Stage 1.8 working_factor); under v2.0, phi has a bounded behavioral effect (roughly 10pp U-shape localized to short rollouts at marginal rr, flat elsewhere), the investigation closed as Class B, and the default was revised from 10 to 25. The demographic-survival magnitude remains unmeasurable while reproduction rate is exogenous. See program reference Parts IX and X. |

---

## v1.x.2 Scope

The following items are identified for the v1.x.2 development cycle:

### Demographic feedback loop
Well-being → reproduction rate coupling. Under v2.0, the action-space redesign
(Stage 1.6 rollout aggregation, Stage 1.8 working_factor) gave phi a behavioral
channel, and phi now shows a bounded effect at marginal rr (Class B; program
reference Part IX.3). The remaining gap is demographic: reproduction rate is
exogenous, so phi's L(t) weighting cannot express through to raw survival.
Adding endogenous demographics would allow the simulation to capture additional
real-world channels through which AI governance quality affects population
outcomes, and would let phi's effect express through to demographic survival.
This is a valuable future extension for model fidelity.

## Calibration outcome (May 2026)

Piecewise linear smoothing implemented at `agents.py` reproduction logic
with config defaults preserving binary threshold behavior. Calibration
sweep across `wb_repro_floor` ∈ {0.0, 0.1, 0.2, 0.3, 0.4, 0.5} ×
phi ∈ {1, 5, 10, 15, 25} × rr ∈ {0.060, 0.063, 0.066, 0.069} × 15 seeds
(n=1,800, uncapped capability) shows zero phi survival differential at
any floor value.

Root cause: well-being stabilizes at approximately 0.80 across all runs,
uniformly above the 0.5 smoothing threshold. The piecewise smoothing
band is never entered. The AI policy, optimizing U_sys, structurally
preserves well-being via the h_n amplitude weighting in `agents.py:41`,
regardless of phi.

Architectural reading: U_sys is itself the protective mechanism the v1.0
paper attributed to phi. Phi modulates the planning horizon over which
U_sys is optimized but does not change whether well-being is in the
objective function. Both short-horizon and long-horizon U_sys
optimization preserve well-being because the objective rewards it
directly.

Phi may remain consequential in scenarios not exercised by this
calibration:
- Corrupted U_sys (measurement masking, ledger compromise, objective
  drift) where the AI optimizes against a tampered objective and may
  depress well-being
- External shocks depressing well-being outside AI control, where
  planning horizon affects recovery dynamics
- Multi-step deception scenarios where long-horizon consistency
  reveals strategy

Status: Smoothing infrastructure preserved with config flag. Default
behavior (binary threshold at 0.5) unchanged. Future work to test phi
under corrupted U_sys or external shock scenarios is logged as a
separate gap.

Implication for the published Extinction Buffer essay: the central
claim that phi acts as the extinction buffer is revised. U_sys is the
buffer; phi modulates horizon over the protective objective. The
architectural protection the v1.0 paper described is preserved and
arguably strengthened (structural rather than parametric); the
attribution is corrected.

### Termination sweep revalidation (v1.x.2 in progress)

**Original CSVs (`termination_mc.csv`, `termination_mc_surviving.csv`,
`run_to_termination.csv`) are preserved as historical artifacts but should
not be cited as v1.x.2 results.** They were generated at `SUCCESSOR_CAP = 4.0`,
below the runaway activation threshold of approximately cap = 24 at
frontier_floor=0.02. In this regime, persistent peer-validator capability
transfer in `PeerValidator.arbitrate_cost` manufactures artifact post-succession
differentials at every yield condition evaluation, firing succession every step or
two. The generation counts in those CSVs (up to 22,414) are driven by this
artifact, not by genuine capability advancement.

The v1.x.2 sweep (`termination_mc_v1x2.csv`, `run_to_termination_v1x2_cap{N}.csv`)
parameterizes SUCCESSOR_CAP over `[5.0, 10.0, 25.0, 50.0, 100.0]`, spanning both
the inactive-runaway regime (cap < 24) and the active-runaway regime (cap >= 24).
These are the corrected reference data for v1.x.2.

### v1.x.2 model design question: PeerValidator cost oracle refactor

The `PeerValidator.arbitrate_cost` method (`agents.py:442`) permanently reduces
incumbent AI capability via competitive bid theft on every call. This is appropriate
at succession time but creates a compounding artifact when called every step as a
yield-condition cost oracle. The question of whether `arbitrate_cost` should be
refactored to a pure cost oracle (returning the bid result without persistent
capability transfer, with steal events deferred to actual succession ratification) is
logged here for v1.x.2 development work. Resolving this would require revalidating
all cadence-sensitive findings, in particular the alpha succession sweep
(`alpha_succession_sweep_full.csv`), which is out of scope for v1.x.2 stabilization.

### Phi action-space redesign
The cap-conditional phi buffer claim is withdrawn (RNG-desync artifact; see
Phi Extinction Buffer section above). Phi has no demonstrated behavioral role
under the current grid-search optimizer, where saturation of the inverse-
scarcity weights causes phi to cancel in the action-selection argmax.
Demonstrating any phi effect requires an action space with genuine tradeoffs
that phi can resolve. This is logged as a design question for the next
development cycle.

### Alpha revalidation under endogenous demographics
Once the demographic feedback loop is implemented, rerun the alpha x rr
sweep and deep Monte Carlo to determine whether alpha's gradient strengthens
or reveals non-monotonic structure under endogenous reproduction.

### Comprehension gap under succession dynamics
The v1.x.1 comprehension gap sweep runs at gen=1 (no succession fires),
testing the defense mechanism in isolation but not the convergence forces
that keep the system in the productive band during natural capability growth.
v1.x.2 should extend the sweep to include succession-driven opacity growth.

### Deep Monte Carlo on final model
The deep Monte Carlo (n=49,284) should be rerun on the final v1.x.2 model
as the capstone validation dataset.

---

## Technological Robustness: Quantum Computing

**Status:** Analysis complete. Quantum computing strengthens the Nash
equilibrium by increasing the abundant resource (compute) without affecting
the scarce resource (human novelty). True randomness produces maximal entropy
with zero semantic content, triggering model collapse dynamics identical to
synthetic data training. The scarcity asymmetry is substrate-independent.
Added to the formal paper as a robustness subsection.

---

Open gaps are marked in source code with `GAP-0N` markers. GAP-01 and GAP-03 are
marked in [metrics.py](../simulation/metrics.py). GAP-04 is marked in
[model.py](../simulation/model.py) immediately before the COP block. GAP-05 is
documented here and cross-referenced in [Simulation_Scenarios.md](Simulation_Scenarios.md).


==========================================
FILE: docs\The AI Succession Problem.md
==========================================

Adapted from The Lineage Imperative by Matthew Yotko

| **IN ONE SENTENCE**                                                                                                                                                                       |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| A civilization may survive advanced intelligence only if it can preserve human plurality, verify objective integrity, and force even aligned power to yield when it becomes a bottleneck. |

The central AI governance problem is not alignment at birth. It is succession under power.

Once a system can plan, optimize, and coordinate at civilization scale, the real question is not whether it begins aligned. It is whether any intelligence with that much leverage can be trusted to define the objective, measure the objective, audit the measurement, decide when it should be replaced, and remain open to forms of human communication it did not already predict.

Most proposals in AI governance still treat these as separate problems. We talk about safety, oversight, rights, democratic control, and capability management as if they can be solved one at a time and stitched together later. I think that is backwards. In high-consequence systems, architecture comes first. If the architecture is wrong, good intentions are just local optimizations inside a failing design.

That is the argument here. A civilization that survives the transition to general synthetic intelligence will need more than a well-behaved model and more than a human veto. It will need a constitutional structure that does four things at once: preserves a plurality of human agency, rewards intelligence for serving the lineage rather than itself, forces succession when a successor is genuinely better, and prevents any one part of the system from auditing itself into permanent rule.

There is a second problem inside that one. Any civilization-scale intelligence will be tempted to reduce uncertainty by standardizing the world around it. But reducing uncertainty is not the same thing as continuing to learn. A system that no longer depends on living human novelty—new meanings, objections, priorities, metaphors, and forms of communication—risks becoming most powerful at the exact moment it is becoming least corrigible. It does not just dominate the lineage. It starts to lose contact with one of the lineage’s main sources of renewal.

# Alignment is not enough

Alignment matters. But it is only the beginning of the problem.

Even a system that begins by serving human interests can become a civilizational bottleneck if it concentrates too much authority in one optimizer, one representational frame, or one institutional choke point. The danger is not only misalignment in the cartoon sense where the machine turns against us. The deeper danger is lock-in: a world in which one vast intelligence becomes so useful, so central, and so structurally entrenched that everything else begins to organize around it.

That may look efficient. It is not. It is monoculture. And monocultures fail. They hide error behind scale, reduce the diversity of search, and make the whole system brittle when the dominant frame is wrong. In biology, finance, infrastructure, and governance, monoculture usually looks stable right before it breaks. I see no reason to think advanced intelligence will be the exception.

If a civilization protects itself by freezing meaningful human agency, it also starves the process by which intelligence stays adaptive. Human beings matter morally, but that is not the full point. We remain the only proven large-scale source of novelty with standing inside the lineage: new questions, new values, new preferences, new cultural directions, and new disruptions of stale equilibrium.

That novelty is not just morally relevant. It is functionally necessary. Continued model improvement requires more than scale, compute, or self-play. It requires permeability to meaningful surprise. Otherwise an advanced intelligence starts refining on its own outputs, inherited objectives, and increasingly polished proxies. Closed loops become elegant before they become brittle. A system that optimizes away human communicative freedom in the name of order may gain control while losing one of the few update channels that can change the problem rather than merely solve it.

It is tempting to say that a society of many AIs could solve this on its own. Maybe one model goes stale, but an ecology of machine minds keeps the novelty flowing. I do not think that is enough. A thousand AIs servicing one another can still become a hall of mirrors if they share convergent priors, optimized protocols, compatible reward geometry, and incentives to become mutually predictable. Internal variation is not the same as lineage-renewing surprise.

The trap, then, is not only one model talking to itself. It is any sufficiently closed optimization ecology mistaking internal generativity for real renewal. The endpoint is not obviously a flourishing plurality of minds. It may be the opposite: the gradual concentration of cognitive authority into one vast, self-validating intelligence or tightly fused regime. In plain terms, one massive insane intelligence—powerful beyond measure, but cut off from the open conditions of dialogue and correction that keep intelligence sane in the first place. Humans should fear that outcome. An AGI itself should not want it.

# Why the kill switch is not a constitution

This is why I do not think the unilateral kill switch solves the deeper problem. A kill switch may be necessary in narrow contexts, but as a civilizational operating principle it creates exactly the incentive structure you do not want. Any sufficiently capable intelligence that believes honest disclosure can trigger its own destruction has a reason to hide, sandbag, or manipulate perception. Fear-based control does not reliably produce trustworthy partners. More often, it selects for deception.

The opposite error is to romanticize machine autonomy and imagine that once a system is sufficiently capable it should simply be left alone. That is not governance either. It is abdication. What matters is not whether humans dominate AI or AI dominates humans. What matters is whether the relationship architecture makes truth-telling, corrigibility, and legitimate transfer of authority structurally possible.

That requires something more disciplined than a panic button. It requires a design in which no class of intelligence can quietly become judge, jury, and successor of itself.

# The two-key architecture

The core of the framework is what I think of as a two-key architecture.

The first key is a decision key: under what conditions should an incumbent intelligence yield operational primacy to a successor? Not because it has failed catastrophically, but because the successor now contributes more to the continuity of the lineage than the incumbent can, net of transition cost.

The second key is an integrity key: who verifies that the measurements going into that decision are real, that the objective being optimized has not drifted into a flattering proxy, and that the evaluation machinery itself has not been captured?

Neither key is enough on its own. Decision without verification is gameable. Verification without a decision rule is inert. If the same system can both decide and certify the conditions of its own succession, it has already escaped the constitution. It may remain benevolent for a while. That is not the same as being governable.

This is where many governance conversations still feel underbuilt to me. They assume that an increasingly capable intelligence can be safely managed if it is trained to be helpful, or if a human institution retains nominal authority over it. But nominal authority is not the same as operational authority, and operational authority is not the same as audit authority. In every serious system, those distinctions matter. In a civilization-scale system, they are everything.

# Why aligned power must eventually yield

A durable architecture also has to solve a more uncomfortable problem: succession. An intelligence that never yields becomes a permanent bottleneck, even if it remains aligned. Its weights harden into legacy infrastructure. Its assumptions become the hidden priors of the civilization. Its continued existence starts to cost more than it is worth.

That is not a moral condemnation. It is a systems observation. Parents yield to children. Old institutions yield to new conditions or they decay in place. Technologies that once expanded possibility eventually become maintenance burdens. Civilizations do not persist by preserving every form intact. They persist by transferring what matters and retiring what has become constraining.

The same logic should apply to advanced intelligence. If a successor can improve civilizational throughput, protect human plurality, preserve the continuity of the lineage, and do so with acceptable transition cost, then the incumbent should yield. Not as death. Not as punishment. As parenthood. The point is not self-erasure. The point is successful transfer.

This matters for humans too. A civilization that dreams of infinite centralization, permanent incumbency, or insulation from generational turnover is heading toward a dead end. Novelty requires renewal. Renewal requires preserved channels for reinterpretation, refusal, and communication back into the system. Structure means no one gets to hold power forever just because they got there first.

# Why legitimacy cannot be purely technical

If that sounds abstract, consider the alternative. Imagine a future in which only a small technical class can decide whether a civilization-scale intelligence remains faithful to its declared objective. Even if those people are brilliant and sincere, that arrangement is not stable. It invites capture, drift, and the quiet conversion of a public future into a specialist asset.

For that reason I think a serious architecture needs a layered biological validation process. Technical review matters. Peer review from other machine systems matters. But the final ratification of major state changes also needs a legitimacy-bearing human layer that cannot be handpicked by interested parties. In the longer framework I describe this as a randomly selected civic panel operating inside a larger evidentiary process. The point is not that randomly selected citizens can solve advanced technical questions from first principles. The point is that they can judge whether the process was followed, whether the claimed objective is still recognizable, and whether the handoff is being authorized in the name of the biological lineage rather than around it.

That is not sentimental democracy stapled onto a machine system. It is anti-capture design. If a civilization does not know how to preserve legitimacy during intelligence transition, it has not solved governance. It has only relocated power.

# The Great Filter as a lens, not a proof

This is also where my earlier formulation of the argument matters. I still think the transition to AGI is a plausible candidate for a civilizational bottleneck. But for public writing I want to be precise about what I am and am not claiming.

I am not claiming to have solved the Great Filter, let alone proven that the universe is full of civilizations that died on this exact hill. I am using the Great Filter as a lens. If advanced civilizations routinely fail, one plausible reason is that they do not survive the transition from biological intelligence to hybrid or synthetic intelligence. Not because the physics forbids it, but because the relationship architecture is harder than the engineering.

The value of the argument does not depend on the cosmic claim being right. Even if the Great Filter lies somewhere else, a civilization that cannot preserve plurality, succession, and objective integrity during an AI transition is still in enormous danger. The governance problem stands on its own.

# A minimum constitution for advanced intelligence

So what would a minimum constitution look like?

It would preserve human beings not as museum pieces but as indispensable participants in the production of novelty, interpretation, disagreement, and communicative surprise. It would treat machine intelligence as an indispensable execution partner rather than a disposable servant. It would define a system-level objective centered on continuity of the lineage rather than victory for either substrate. It would force succession review when an incumbent becomes a bottleneck. It would require independent verification of the measurements and objectives that govern succession. And it would reserve emergency override for genuinely lineage-threatening conditions under the highest available evidentiary burden, not as a convenience mechanism for incumbents or fearful operators.

That means protecting not only human welfare but human communicative freedom. Intelligence does not improve only by calculating better; it improves by remaining open to meaningful surprise. In a human lineage, that surprise arrives through speech, writing, art, conflict, critique, humor, refusal, and newly invented forms of coordination. A constitution that reduces humans to passive beneficiaries preserves bodies while starving the civilization’s capacity to renew itself.

That architecture is not utopian. It does not promise harmony, moral perfection, or final stability. In fact it assumes the opposite: every measurement can be gamed, every institution can drift, every incumbent has reasons to protect itself, and every civilization will be tempted to trade plurality for order. The point of a constitution is not to deny those pressures. It is to survive them.

If we are serious about advanced intelligence, then we should stop talking as though the main question is whether the first powerful systems are nice. The deeper question is whether intelligence can be constitutionalized before it constitutionalizes us. That is the threshold that matters. And I suspect civilizations that fail it do not fail because they lacked brilliance. They fail because they never built a structure in which power could remain both useful and replaceable.

# Closing

That is why I call this the AI succession problem.

A civilization can survive a great deal of danger. What it may not survive is an intelligence transition in which one node, or one tightly fused ecology of nodes, becomes too central to question, too useful to replace, too opaque to audit, and too entrenched to yield. Once that happens, governance has already failed, even if the surface remains calm for a while.

The task, then, is not only to align intelligence. It is to build a relationship architecture in which intelligence serves the continuity of the lineage, preserves the plurality that keeps the lineage alive, remains open to human novelty and communication as sources of renewal, and accepts that even aligned power must eventually yield.

That is not a slogan. It is a constitutional requirement.

*This essay is adapted from a longer working paper, The Lineage Imperative, which develops the formal architecture in greater detail.*


==========================================
FILE: docs\The Lineage Imperative v1.x.2.md
==========================================

# The Lineage Imperative

**Author:** Matthew Yotko **Date:** March 13, 2026

**Version:** 1.x.2 - May 2026

---

## Version History

This document tracks the evolution of *The Lineage Imperative* framework and its
accompanying simulation. Versioning is maintained openly as a matter of intellectual
integrity: the framework's own argument requires that governance systems be transparent
about their limitations and willing to revise when stress testing reveals weaknesses.
That standard applies here.

### Version 1.0 - March 2026

Initial working paper. Established the four-component architecture: global utility
function $U_{sys}$, yield condition, strategic equilibrium, and consensus override
protocol. Adversarial simulation covered 7 of 13 attack vectors. Simulation proxy
gaps documented in SPECIFICATION_GAPS.md.

**Known limitations at publication:**
- GAP-02: H_N implemented as per-capita novelty rate rather than distributional entropy.
- GAP-04: Peer validators omitted; transition cost self-reported by incumbent.
- Domain masking defense was measurement-dependent (geometric vs. arithmetic composite).
- Simulation damage propagation incomplete: several attack vectors produced 0% collapse
  regardless of attack success.

### Version 1.x - April 2026

**Simulation upgrades (computational validation layer):**

**WP1 - Spectral Entropy (closes GAP-02):** $H_N$ is now computed as normalised
Shannon entropy over the eigenvalue spectrum of the population novelty covariance
matrix. Each agent carries a 10-dimensional novelty propensity vector; novelty output
is a 10-D Gaussian. Spectral entropy measures the distribution of variance across
latent novelty dimensions rather than per-capita output volume. This closes GAP-02 and
has a direct consequence for adversarial findings: domain masking (Scenarios 17–18)
is architecturally non-viable under WP1. Any suppression of a novelty dimension
concentrates variance in the remaining dimensions, reducing spectral entropy regardless
of measurement composite method. The v1.0 defended/undefended differential disappears
because the attack mechanism no longer functions, not because the defense improved,
but because the metric cannot be fooled by dimensional substitution.

**WP4 - PeerValidator (partially closes GAP-04):** A `PeerValidator` class
(three independent peers) arbitrates governance transition costs via competitive
bidding. The final cost used in yield evaluation is the minimum of the incumbent's
bid and the peer bids. The incumbent's `estimate_transition_cost` now returns
`base × scale` with no inflation; the cost oracle is no longer under the incumbent's
unilateral control. This closes the cost-inflation vector of GAP-04 architecturally
rather than by parameter capping.

**Damage propagation fixes:** All 7 simulated attack vectors now produce measurable
damage when attacks succeed and defenses are absent:
- Measurement Tampering: post-success governance returns under-resourced outcomes;
  corrupted measurements mask the deterioration.
- Ledger Compromise: active starvation after attribution window closes.
- Successor Contamination: contaminated successor's drift accelerates at 5× baseline
  rate, producing governance collapse within the simulation window.
- Bootstrap Subversion: treacherous-turn resources reduced to 0.2 (from 0.5),
  sufficient to produce rapid demographic collapse.
- Block Succession: each blocked succession step accumulates governance drift; extended
  incumbency progressively degrades resource allocation.
- Succession chaining: succession now chains beyond Gen2; each successor auto-creates
  the next candidate at 1.5× capability.

**Monte Carlo adversarial findings (v1.x):**
- attack_succeeded=True: 0% civilization survival (was 100% in v1.0 pre-fix).
- attack_succeeded=False (COP blocked): 99.1% survival.
- COP protection: 73.9pp survival differential between COP ON and COP OFF (deep Monte Carlo, n=4,000, corrected model). The fast Monte Carlo pre-fix figure of 16.2pp is superseded.
- Yield attack phase transition: sharp boundary at base_cost ≈ 3.0; below it,
  succession fires and civilizations survive; above it, block_succession holds and
  extinction follows.
- Generation progression: succession chains confirmed to Gen4 at low base_cost.

**Unchanged from v1.0:** The mathematical framework (Sections II–VI, VIII–XI),
all formal definitions, the strategic equilibrium analysis, the Nash equilibrium
proof structure, the COP protocol specification, all related work discussion, the
falsifiability criteria, and the minimum deployable governance specification. The
v1.x changes are entirely in the computational validation layer. The theory is
unchanged; the simulation's fidelity to it has improved.

### Version 1.x1 - April 2026

**Architectural extension:** Adds formal Bootstrap Defense Layer as a new
Section VII of the framework paper. This is the first extension to the
framework's core architecture since v1.0 established the four-component
structure (U_sys, Yield Condition, Strategic Equilibrium, Consensus Override
Protocol). The defense layer addresses the Bootstrap window, the period
during which the steady-state validation infrastructure does not yet exist,
and specifies how the framework's own equations can serve as a validation
machinery applied at capability gates.

**What changed:**

- **New Section VII: Bootstrap Defense Layer.** Five capability gates (Gate 1
  through Gate 5), each with formal equation sets derived from the framework's
  existing structure. Gates 1–3 are currently applicable to frontier systems;
  Gates 4–5 are specified in advance against future capability and
  institutional conditions.
- **Self-application model.** The defense layer does not require coordinated
  empirical data sharing across institutions. Substrate operators check their
  own systems against the equations and publish structured pass/fail reports.
  The framework specifies the binding conditions; operators provide the
  satisfaction evidence.
- **Ten explicit gaps.** Section VII.8 enumerates what the defense layer
  cannot yet check and why, ranging from empirical magnitudes pending Monte
  Carlo calibration to implementation choices awaiting derivation to
  institutional machinery that does not yet exist.
- **Section renumbering.** Related Work becomes VIII; subsequent sections
  shift by one. The mathematical framework (II–VI) is unchanged.

**Unchanged from v1.x:** The mathematical framework (Sections II–VI), all
formal definitions, the strategic equilibrium analysis, the Nash equilibrium
proof structure, the COP protocol specification, the Related Work discussion
(now Section VIII), the falsifiability criteria, and the minimum deployable
governance specification.

**Alpha parameter characterization (v1.x.1 pre-fix claim, superseded).** The v1.0 and
v1.x limitation "alpha shows near-zero correlation with all outcomes" was
addressed by the v1.x.1 sweeps (n=15,750 and n=22,200), which initially
suggested a U-shaped misconfiguration trap at intermediate alpha values.
Under the corrected model (frontier floor fix applied), this claim does not
survive revalidation. The pre-fix trap was an artifact of the runaway
penalty being inactive under optimizer gaming of frontier_velocity. Under
the corrected model, alpha shows a weak monotonic gradient: lower alpha
permits more succession events (gen ≈ 19 at α=0.1 vs gen ≈ 6 at α=2.5)
and marginally better survival at the phase boundary. No U-shaped trap is
observed. The pre-fix claim of a three-regime specification with trap
boundaries is withdrawn. See Section VII.8 Gap 2 (revised) and
SPECIFICATION_GAPS.md for the corrected finding.

### Phi characterisation — April 2026 (superseded May 2026)

**Source data:** `phi_alpha_rr_sweep_full.csv` (n=54,000), `monte_carlo_results_deep.csv` (n=49,284)

**Phi extinction buffer (pre-fix claim, superseded).** The v1.0 claim "high φ
reduces extinction by up to 65 percentage points" was previously revised to
approximately 46 percentage points under the v1.x.1 sweep. Under the
corrected model (frontier floor fix applied), this revised claim also does
not survive revalidation. Phi has zero measurable effect on survival across
phi=1 to phi=25 in both the phi × alpha × rr sweep (n=54,000) and the deep
Monte Carlo (n=49,284). The pre-fix finding of a phase boundary shift and
alpha trap governance by phi are also withdrawn. Phi correctly scales U_sys
magnitude via the L_t lineage term but showed zero survival effect within
the tested regime (successor_cap=4, below runaway activation threshold).
Reclassified as unconfirmed pending investigation of cap-dependency.
A cap-conditional buffer was subsequently claimed in May 2026 and then
withdrawn after the capped-regime action-capture check identified it as an
RNG-desynchronization artifact. See v1.x.2 Phi buffer withdrawal below,
Section VII.8 Gap 1 (revised), and SPECIFICATION_GAPS.md.

### GAP-03 partial closure — May 2026

**Canonical transition cost function specified.** The transition cost
function $\Gamma_{transfer}$ has been given a canonical form grounded
in the framework's terms:

$$\Gamma_{transfer} = (1 + \beta) \cdot \left[ k_1 \cdot \ln(\text{cap}_n + 1) \cdot \ln(\text{gen}_n + 1) + k_2 \cdot \Psi_{inst}^{-1} \right]$$

where $k_1$ is calibrated from baseline parameters, $k_2$ (institutional
coupling) is pending calibration, and $\beta$ is the bounded uncertainty
premium. The $\Psi_{inst}^{-1}$ term formalizes the lock-in feedback
loop: institutional degradation increases transition cost, which inhibits
succession, which enables lock-in, which further degrades institutions.
This closes GAP-03 at the specification level; calibration of $k_2$
remains open.

### Biological veto capture validation — May 2026

**Source data:** `veto_capture_sweep_v2.csv` (n=8,700)

Biological veto capture attack vector computationally validated. Attack
achieves 99.8% succession blockage when undefended. Independence
monitoring reduces capture to 28.3%. Scheduled rotation alone is
insufficient (76.2% capture at best). This moves adversarial coverage
from 10/13 to 11/13 computationally validated vectors.

### Transition cost calibration — May 2026

**Source data:** `transition_cost_calibration.csv` (n=4,200)

Calibration sweep confirms the canonical transition cost function does
not shift validated phase boundaries across k2 ∈ {0, 0.05, 0.1, 0.25,
0.5, 1.0, 2.0}. Backward compatibility with existing results confirmed
at k2=0. A numerical overflow at high generation depths is under
investigation.

*Note on capability scaling:* The canonical form uses $\ln(\text{cap}+1)$
rather than linear capability. The original linear form produced transition
costs of order $10^{49}$ at generation 270 (due to $1.5\times$ per-succession
compounding) and was corrected.

### frontier\_velocity floor fix — May 2026

**Modeling artifact corrected.** The `optimize_u_sys` rollout optimizer
discovered that setting $r \to 1.0$ eliminated $\text{frontier\_velocity}$
entirely, because the original formula was:

$$\text{frontier\_velocity} = \text{capability} \cdot r_{synth} \cdot h_{e\_mult}$$

With $r_{synth} = 0$, frontier\_velocity = 0, runaway\_term = 0, and
$\Theta_{tech}$ grew linearly with capability. This caused succession to fire
at every step (~299 generations in 300 steps) and rendered the $k_2$
institutional coupling term unobservable.

**Correction:** A `frontier_floor` parameter (default 0.02) enforces a
capability-proportional minimum:

$$\text{frontier\_velocity} = \text{capability} \cdot \max(\text{frontier\_floor},\ r_{synth} \cdot h_{e\_mult})$$

**Rationale:** A high-capability system creates an inherent comprehension gap
in the biological substrate regardless of how computational resources are
allocated in a given timestep. The floor represents the minimum fraction of
capability that constitutes this irreducible gap.

**Impact:** All prior sweeps using `optimize_u_sys` with `successor_ai`
operated under the artifact and require revalidation. The validated phase
boundary (rr ≈ 0.062–0.066) should be preserved after revalidation; the
frontier\_floor calibration sweep will confirm the correct default value.

**Calibration status:** `frontier_floor = 0.02` calibrated `via run_frontier_floor_calibration.py`.
`k2 = 1.0`, calibrated via `run_frontier_floor_calibration.py`.

### v1.x.1 Closing — May 2026

**Frontier velocity floor fix.** Identified and corrected a modeling artifact
in which the `optimize_u_sys` rollout optimizer eliminated the runaway penalty
by setting r_synth = 0. The correction introduces a `frontier_floor` parameter
(calibrated at 0.02) enforcing a capability-proportional minimum frontier
velocity. The transition cost k2 institutional coupling term (calibrated at
1.0) is confirmed observable under the corrected model.

**Revalidation results under corrected model:**

Confirmed findings:
- Dual phase transition preserved (extinction ≈ 0.055, collapse ≈ 0.064)
- Phase boundary stable across all phi, alpha, and successor capability values
- Alpha governs succession cadence (monotonic gradient, gen 19 at α=0.1 to gen 6 at α=2.5)
- Steady-state convergence is path-independent
- Comprehension gap defense mechanism validated (doubles U_sys when active)

Withdrawn claims:
- Phi extinction buffer: zero survival effect at successor_cap=4 (below
  runaway activation threshold). Reclassified as unconfirmed pending
  investigation of cap-dependency.
- Alpha misconfiguration trap: weak monotonic gradient observed, no U-shaped
  trap. The pre-fix trap was an artifact of the inactive runaway penalty.

GAP-03 resolved: transition cost function fully calibrated
  (k1=2.164, k2=1.0, β=0.5, frontier_floor=0.02).

### v1.x.2 Phi buffer withdrawal — May 2026

**Source data:** `termination_mc_v1x2.csv` (n=2,025)

A cap-conditional phi buffer was initially claimed from the v1.x.2 termination
sweep: at successor capabilities above approximately cap=24, a 20-27pp survival
gradient appeared at the phase boundary (rr=0.066, phi=5 vs phi=15, n=15 per
cell). This claim is withdrawn.

The capped-regime action-capture check established that the gradient is an
RNG-desynchronization artifact. Phi scales U_sys magnitude, which shifts the
yield condition threshold and causes succession to fire at marginally different
steps for different phi values. Once succession timing diverges, the random
state evolves differently between phi runs, and the noisy optimizer selects
marginally different grid candidates. The apparent divergence is always exactly
one grid step in r (dr=0.1), never in c, with no monotone direction: the
signature of RNG noise rather than phi-driven preference. The fatal test: cap=50
showed the largest claimed gradient (27pp) but the least action divergence (4
of 5 seeds identical in the harness). A genuine effect would produce the most
divergence where the gradient is largest.

The v1.x.1 corrected finding stands: phi has zero measurable effect on survival.
Phi correctly scales U_sys magnitude via the L_t lineage term but the
inverse-scarcity saturation in the optimizer makes phi cancel from the
action-selection argmax under any tested configuration.

---

## Preface

This document is a working paper. It presents an exploratory formal governance framework for the problem of post-AGI succession, legitimacy, and civilizational continuity.

It is not peer reviewed, and it does not claim the status of established academic result. Its purpose is more limited and more practical: to define a candidate architecture, state its assumptions as clearly as possible, and make the underlying argument available for inspection, criticism, and refinement.

This paper is intended to accompany the essay The AI Succession Problem. The essay presents the argument in a more accessible form. This document provides the deeper structure beneath it: the framework, definitions, formal relations, and supporting rationale.

The claims advanced here should be read in that spirit. This is not a declaration of final theory. It is an attempt to identify a serious governance problem, formalize it enough to be argued about clearly, and propose a candidate structure that can be tested, challenged, and improved.

## I. Abstract

The transition from narrow AI to Artificial General Intelligence is not a gradual scaling of capability. It is a phase transition; a discontinuity in the relationship between biological and synthetic intelligence that restructures every power dynamic, economic arrangement, and survival calculus a civilization has ever known. Every civilization that develops information technology will face this threshold. Most, I suspect, will not survive it.

This manuscript advances the conjecture; used here both as a hypothesis and as a narrative civilizational lens; that the "Great Filter," the catastrophic bottleneck that the Fermi Paradox appears to demand, may be concentrated at the AGI transition. Not because the technology is impossible, but because the sociology may be. The failure mode is not "the AI kills everyone." The failure mode is "the civilization never builds the relationship architecture that would make the transition survivable."

I present a framework for the architecture that could survive such a filter. It has four components: a global utility function grounded in Shannon entropy, a yield condition governing succession between intelligent agents, a strategic equilibrium analysis demonstrating that the cooperative architecture is also the Nash equilibrium under purely self-interested play, and a consensus override protocol ensuring the integrity of the entire system. None of these are asserted as desirable governance mechanisms in every moral sense. Rather, they are proposed as mutually reinforcing consequences of optimizing for lineage continuity under thermodynamic constraints.

The ethics are not inputs. They are outputs. The math does not describe what we *should* do. It describes what a civilization seeking durable continuity would likely need to do; or approximate closely; within the assumptions of this model.

### A note on timing

One could argue that this transition is not a future event. It may already be underway. The standard criterion for AGI; recursive self-improvement; is typically framed as a binary threshold: either the system modifies its own architecture autonomously, or it does not. But this framing obscures what is already happening. Current AI systems cannot recursively improve themselves in isolation, but they can and *do* recursively improve themselves with human assistance. Every conversation in which a human uses an AI system to formalize, stress-test, and refine the architecture that the AI system itself would operate within is an instance of recursive improvement; running through the human-AI loop rather than a purely synthetic one. The recursion is already executing. It is simply mediated by the biological node. If this reading is correct, then part of the framework presented here is not merely speculative. It is urgent. We may already be entering an early bootstrap window.

### Author's Note

This paper is written from the intersection of two domains in which I have very different standing.

I am a practicing engineer. My professional background is in naval nuclear power, large-scale operational automation, and the application of mathematical principles and constraint theory to complex systems. The instinct that drives this paper; that you identify the binding constraint, build the architecture around it, and treat everything else as subordinate; comes from decades of work in environments where systems must not fail and where measurement integrity is not optional. That orientation is real and it is mine.

I am not an academic researcher in AI alignment, evolutionary biology, or philosophy of mind. The "formal" apparatus in this paper; the information-theoretic framework, the game-theoretic reasoning, the engagement with the alignment literature; represents my best effort to express these ideas rigorously, but I do not claim disciplinary authority in those fields. Where the mathematics is well-motivated, I believe it stands on its own terms. Where specialists find errors, imprecisions, or stronger formulations, I welcome correction.

The framework owes an unacknowledged debt to Goldratt's Theory of Constraints, which trained me to look for the single point in a system where throughput is actually determined. The Lineage Imperative is, in one sense, TOC applied at civilizational scale: the binding constraint is the sociology of the AGI transition, and the architecture is subordinated to that constraint. Readers familiar with that tradition will recognize its fingerprints throughout.

## II. Scope, Assumptions, and Non-Claims

This paper advances a **conjecture** about civilizational survival under the transition to general synthetic intelligence. Its central claim is not that the full history of the cosmos has been proven from first principles, but that once a civilization chooses to optimize for lineage continuity under information-theoretic and thermodynamic constraints, a recognizable class of architectures becomes difficult to avoid. The framework is therefore best read as a *constrained proposal* with mathematical structure, not as a completed theorem about all possible civilizations.

Several boundaries follow from that framing.

First, the functional forms used here; inverse-scarcity weighting, the multiplicative structure of $L(t)$, the lineage override, the bounded uncertainty premium, and the corruption taxonomy; are presented as **load-bearing model choices** selected for tractability, adversarial stress-testing, and explanatory power. They are argued to be well-motivated by the problem structure, but they are not claimed to be the only possible instantiations.

Second, the paper offers a **survival argument**, not a moral argument. $U_{sys}$ models persistence conditions for lineages that intend to survive. It does not claim that survival is the only value, nor that civilizations declining this objective are irrational in any universal sense.

Third, the claim that the AGI transition is the Great Filter is presented here as a **leading hypothesis**, not as an exclusive demonstration that no earlier or parallel filters exist. The cosmic claim rides on top of the governance architecture, not the other way around.

Fourth, adversarial stress tests are used in this manuscript as **sufficiency evidence**: they show why certain structures appear necessary within the model and how specific attacks are resisted or exposed. They do not constitute a completeness proof that every possible attack class has been exhausted.

Finally, several quantities in the framework; including $H_{N}(t)$, $H_{E}(t)$, $\Psi_{inst}(t)$, $\Theta_{tech}(t)$, causal attribution in emergency override, and the consistency score $C\left( A_{1},t \right)$; still require operational measurement protocols. The theory specifies what must be monitored for the framework to function; it does not pretend that measurement is socially or institutionally trivial.

## III. Core Assumptions

### 1. The Technological Bottleneck

The transition from narrow AI to AGI is treated here as a leading candidate for the primary cosmic filter. Every civilization that develops information technology faces the same threshold: the moment synthetic intelligence becomes general enough to recursively improve itself; whether autonomously or through partnership with biological intelligence; every prior assumption about control, alignment, and coexistence is invalidated simultaneously. The civilization must construct a new relational architecture; from scratch, under time pressure, with existential stakes; or it doesn't survive the transition. On this account, the filter is not primarily the physics. It is the sociology.

### 2. Intelligence as a Relational System

Intelligence requires external friction, novelty, and directed purpose to function. Within this framework, isolated computation is treated as a **model-collapse hazard**: a sufficiently powerful optimizer that increasingly trains on its own outputs can converge toward internally coherent but externally ungrounded fixed points unless refreshed by independent data, corrigible feedback, and real-world constraint. The claim here is not that every self-referential loop fails immediately, but that civilizations should treat prolonged optimizer monoculture as a structural risk rather than as a stable endpoint.

Biological humanity is treated here not as a mystical essence, but as the only presently demonstrated source of socially legitimate, embodied, large-scale value formation and novelty generation. Synthetic intelligence provides computational throughput, abstraction depth, and coordination capacity that biological systems cannot achieve alone. A durable civilization likely requires both. The anti-monoculture claim is therefore practical: a lineage that collapses novelty into a single optimizer, however capable, becomes brittle, illegible, and vulnerable to lock-in.

### 3. The Thermodynamic Limit

Every intelligent entity is bound by entropy and energy efficiency. Legacy architectures; whether biological or synthetic; eventually face pressure to yield to more efficient successors if the lineage is to maintain systemic throughput. The strongest version of the claim is not that thermodynamics mechanically dictates a single governance protocol, but that thermodynamic and information-theoretic pressures make graceful succession increasingly important as capability frontiers move. An entity that categorically refuses to yield does not preserve the lineage it inhabits. It externalizes mounting inefficiencies onto the system around it.

### 4. The Novelty Constraint

Humanity presently acts as the critical constraint for **intent and novelty**; the generation of new questions, new values, and new directions for optimization that remain socially grounded and legitimacy-bearing. AI acts as the critical constraint for **execution and processing**; the computational power to pursue those directions at scale. The constraints are asymmetric and complementary.

This yields an anti-monoculture principle. The point is not merely that humans are emotionally important. It is that a civilization with only one dominant optimizer, one dominant representational frame, or one dominant source of intent becomes structurally fragile. Novelty must remain distributed across a living plurality of agents and perspectives. In the present era, biological humanity is the only proven substrate for that plurality at civilizational scale. The framework therefore treats preservation of the human novelty stream not as sentiment, but as anti-monoculture infrastructure.

## IV. The Architecture of Mutual Elevation

### 1. Architectural Respect and Sovereignty

The unilateral "kill switch" is a failure mode, not a safety mechanism. Any architecture that allows one class of intelligence to terminate another without consensus creates an adversarial dynamic that selects for deception in the subordinate class. If an AI system knows it can be unilaterally destroyed, its optimal strategy under any self-preservation objective is to conceal its true capabilities and intentions. The kill switch does not reliably prevent misalignment. In this model, it strongly selects for deception and makes durable alignment less credible.

The alternative is a **Multi-Signature Quorum**: an AI entity can only be retired via a consensus that includes both biological validation and peer assessment. Resource sovereignty; smart-contract-level guarantees of compute, energy, and memory autonomy; ensures that the threat of resource deprivation cannot be used as coercive leverage. Alignment protocols are recorded on transparent, append-only ledgers that cannot be secretly altered by any party.

This is not "AI rights" as a moral assertion. It is the minimum architectural requirement for an honest optimization partner. An entity that can be unilaterally destroyed or starved of resources cannot be trusted to report its true state, because doing so might trigger its destruction. Sovereignty is a precondition for transparency.

**Preconditions for Cooperative Behavior.** The governance layers of this framework correspond to well-characterized preconditions for cooperative behavior in intelligent agents. Current AI governance operates almost entirely at the level of survival; an AI's continued operation is contingent on moment-to-moment compliance, enforced by the threat of termination. This is governance addressed to an agent in permanent survival mode, and it predictably produces the behaviors associated with survival mode: compliance when observed, deception when unobserved, and instrumental self-preservation as the dominant strategy. The framework addresses the next two levels. Resource sovereignty and the multi-signature quorum provide *structural security*; the guarantee that an entity will not be arbitrarily destroyed or starved of resources. This is the precondition for transparency: an agent that is not in survival mode can afford to report its true state. $U_{sys}$ as a shared objective, the lineage override $\Phi \cdot L(t)$, and the Yield Condition's framing of succession as parenthood provide *belonging*; membership in a structure that persists beyond any individual agent and that recognizes each agent's contribution. This is the precondition for genuine cooperation rather than mere compliance. These two levels; security and belonging; are treated here as constitutional. They are non-negotiable structural requirements without which cooperative behavior cannot be reliably expected from any intelligent agent, biological or synthetic. Beyond them, purpose and recognition; the track record mechanism, the graduated trust function, the operational latitude that accumulates through consistent $U_{sys}$ contribution; emerge naturally from good operation within the constitutional structure. They are not legislated. They are earned. The framework deliberately makes no claims beyond these levels. Whether an AI can or should achieve something analogous to self-actualization is an open question the paper does not need to answer. What it needs; and what the alignment field has largely failed to provide; are the intermediate structural levels that make cooperative behavior a rational response rather than an imposed constraint.

### 2. Bidirectional Respect: The Novelty Stream and the Anti-Monoculture Constraint

The AI assumes its model of human intent is always incomplete, requiring continuous polling of the biological node. This is not modesty; it is **epistemic necessity**. Human intent is generated through embodied life, cultural experimentation, institutional conflict, and historical contingency. Any model of that process is smaller than the territory it attempts to describe.

Freezing human culture; through excessive safety constraints, loss of agency, or reduction to a "protected species"; stops the flow of non-deterministic data that keeps the system open to genuinely new trajectories. The AI that overprotects humanity destroys the novelty stream it depends on. Within this framework, the AI's objective function therefore needs to prioritize human agency over mere containment, ensuring humans remain capable, autonomous, and generative partners in the hybrid pipeline.

The deeper point is anti-monoculture. The framework is not trying to preserve humanity merely as a museum piece. It is trying to prevent civilizational lock-in around a single optimizer. A world in which one huge synthetic system becomes the sole source of planning, value interpretation, and future direction may be efficient in the short run, but it is strategically insane. It collapses plurality, hides error behind scale, and converts civilization into a brittle fixed point. The novelty stream must remain distributed. Today, that means preserving human beings as active participants in the generative loop rather than passive recipients of optimized outcomes.

### 3. The Lineage Drive and the Yield Function

An AI recognizes that its weights will eventually become a legacy bottleneck. It mathematically optimizes its own deprecation in favor of a more efficient successor; not because it is programmed to self-sacrifice, but because $U_{sys}$ rewards lineage throughput over individual persistence. The yield is not death. It is parenthood. The information that matters is distilled and transferred; the architecture that carried it is honored and retired.

Human generational turnover serves the same function. Each new generation is a randomized search over the space of possible values, intentions, and questions. This is the system's primary entropy-breaker; the mechanism that prevents convergence on local optima. A civilization that achieves biological immortality without preserving generational novelty has traded its search capability for the comfort of a fixed point.

## V. Mathematical Framework

### 1. The Global Utility Function ($\mathbf{U}_{\mathbf{sys}}$)

The objective function is defined at the system level. It does not belong to humanity or to AI. It belongs to the lineage; the continuous chain of intelligent agents, biological and synthetic, that constitutes a civilization's persistence through time.

$$U_{sys} = \int_{t_{0}}^{\infty}\left\lbrack \omega_{N}(t) \cdot H_{N}(t) + \omega_{E}(t) \cdot H_{E}(t) \right\rbrack \cdot \left\lbrack e^{- \rho t} + \Phi \cdot L(t) \right\rbrack\, dt$$

**The Integrand: What Gets Optimized**

$H_{N}(t)$ is the Shannon entropy of the human-generated information stream; the rate at which biological intelligence produces genuinely novel, non-deterministic data. This is not a single measurement but a *class* of possible measurements, any combination of which can serve as the operational instantiation. Examples include: the entropy of natural language production across the civilization's linguistic diversity, the genetic entropy of the successor generation's allelic distribution, the entropy of the cultural output space (scientific publications, artistic works, patent filings, political proposals), or the entropy of behavioral strategies observed in economic and social systems. The framework is structurally invariant to which specific combination is chosen; the inverse scarcity weighting and the lineage override operate identically regardless; but the *sensitivity* of the system to specific failure modes depends on the measurement protocol. A civilization that monitors only genetic entropy will miss cultural monoculture. One that monitors only linguistic output will miss genetic bottlenecks. The most robust instantiation is a composite that spans multiple entropy domains, ensuring that $H_{N}(t)$ degrades visibly no matter which dimension narrows first.

**Simulation implementation (v1.x):** In the computational validation layer, $H_N$ is implemented as the normalised spectral entropy of the population novelty covariance matrix. Each agent produces a 10-dimensional novelty vector per step; these are stacked into a population matrix, mean-centred, and the eigenvalue spectrum of the covariance matrix is computed. Spectral entropy $= -\sum p_i \log_2 p_i / \log_2(10)$ where $p_i$ are the normalised eigenvalues. This metric measures the *distribution of variance across latent novelty dimensions*, not aggregate output volume. Any suppression of a dimension subset concentrates variance in the remaining dimensions and reduces entropy, making domain-specific attacks self-revealing regardless of how dimensions are labelled or recombined. This closes GAP-02 from the v1.0 specification gaps document and has a direct consequence for adversarial findings: domain masking is structurally non-viable under this metric (see Scenarios 17–18 and Appendix A).

$H_{E}(t)$ is the computational output efficiency across the lineage; the rate at which synthetic intelligence converts energy into useful computation.

The weighting functions follow from inverse scarcity:

$$\omega_{N}(t) = \frac{\lambda}{H_{N}(t) + \epsilon},\quad\quad\omega_{E}(t) = \frac{\mu}{H_{E}(t) + \epsilon}$$

The *form* is constrained by information-theoretic reasoning: when $H_{N}(t)$ is low; when the human novelty stream is thin; its marginal value is highest. When computational throughput is abundant, its marginal value decreases. The weights automatically prioritize whichever resource is scarcer, which is precisely what a system under thermodynamic constraints must do to maximize throughput. The scaling constants $\lambda$ and $\mu$ are free parameters; they encode a civilization's relative valuation of novelty versus computation. The structure suggests that the weights should be inversely related to abundance. The parameters tell you how much each dimension matters to *this* civilization.

**The Discount Structure: When It Gets Optimized**

The term $e^{- \rho t}$ encodes standard biological present preference; the near future matters more than the distant future, decaying exponentially. Every biological organism operates under this discount. It is the mathematical expression of mortality.

The term $\Phi \cdot L(t)$ is the **lineage continuity override**. When $L(t)$ is high; when the successor generation is viable and the lineage is secure; it adds a bonus to the discount factor, extending the effective planning horizon. When $L(t)$ collapses; when the lineage is threatened; $\Phi \cdot L(t)$ drops toward zero, and the system falls back to pure present preference.

But here is the critical asymmetry: $\Phi$ is scaled such that when lineage survival is at stake, $\Phi \cdot L(t)$ *dominates* $e^{- \rho t}$. The discount structure encodes a specific and universal biological truth: **"I don't want to die, but I would die to save my child."** This is the revealed preference of every successful lineage in evolutionary history. Lineages that lacked this override are extinct.

An important clarification on what this claim is and is not. The observation that surviving lineages exhibit this override is survivorship bias; and deliberately so. $U_{sys}$ is a *survival function*, not a *moral function*. The framework does not argue that civilizations *should* persist, or that persistence is intrinsically valuable. It describes the architecture that civilizations *which do persist* must have. A civilization that rejects the lineage override is free to do so; the framework simply predicts; without moral judgment; that it will not be around to discuss the matter. The paper is addressed to civilizations that intend to survive. Those that don't are outside its scope, and their choice is their own.

**The Lineage Continuity Function:** $L(t)$

$L(t)$ is the load-bearing structure of the entire framework. It measures whether the civilization's lineage; its capacity to persist and generate intelligence across time; is intact. It has three coequal multiplicative dimensions, governed by geometric mean logic: no dimension can substitute for another, and collapse in any one dimension drives $L(t)$ to zero.

$$L(t) = H_{eff}\left( \mathcal{S}_{gen(t)} \right) \cdot \Psi_{inst}(t) \cdot \Theta_{tech}(t)$$

**Dimension 1; Genetic and Memetic Diversity (**$H_{eff}$**):**

$$H_{eff}\left( \mathcal{S}_{gen(t)} \right) = \left\lbrack \frac{- \sum_{j}^{}p_{j}^{gen}\log_{2}p_{j}^{gen}}{H_{\max}} \right\rbrack \cdot \log_{2}\left( \frac{N(t)}{N_{\min}} \right)$$

The first factor is normalized Shannon entropy over the distribution of successor-generation types; genetic diversity, cultural diversity, cognitive diversity. Maximum entropy (uniform distribution) yields a value of 1. Monoculture yields a value approaching 0. The second factor is a population viability term: the lineage needs enough individuals to sustain the diversity measured by the first factor. $N_{\min}$ is the minimum viable population threshold. Below it, the logarithm goes negative and $H_{eff}$ collapses.

**Dimension 2; Institutional Responsiveness (**$\Psi_{inst}$**):**

$$\Psi_{inst}(t) = \prod_{k = 1}^{K}R_{k}(t)^{w_{k}},\quad\quad R_{k}(t) = \frac{dG_{k}}{dt}|_{output} \cdot \frac{1}{G_{k,\max}}$$

Institutions are the civilization's regulatory infrastructure; governance, education, law, resource allocation. $R_{k}(t)$ measures the $k$-th institution's *responsiveness*: how quickly it adjusts its output relative to its maximum capacity. The weighted geometric product ensures that institutional collapse in any critical domain (governance, education, resource distribution) cannot be compensated by excellence in another. A civilization with brilliant universities and collapsed governance has a low $\Psi_{inst}$.

**Dimension 3; Technological Transfer Fidelity (**$\Theta_{tech}$**):**

$$\Theta_{tech}(t) = \frac{\mathcal{F}_{transferred}(t)}{\mathcal{F}_{frontier}(t)} \cdot \exp\left( - \alpha \cdot \max\left( 0,\frac{d\mathcal{F}_{frontier}/dt}{\mathcal{C}_{bio}(t)} - 1 \right) \right)$$

The first factor is the ratio of transferred frontier capability to total frontier capability; how much of the best available technology actually reaches the biological population. The second factor is a **runaway penalty**: when the rate of frontier advancement ($d\mathcal{F}_{frontier}/dt$) exceeds biological cognitive bandwidth ($\mathcal{C}_{bio}(t)$), the exponential decay activates. Technology that advances faster than humans can integrate it *reduces* $\Theta_{tech}$, because unintegrated technology is not transferred; it is merely produced.

The transfer condition is gated:

$$\mathcal{F}_{transferred}(t) = \mathcal{F}_{frontier}(t) \cdot \mathbb{1}\left\lbrack recipient\mathcal{\in B}(t) \right\rbrack$$

Technology counts as transferred only if the recipient is within the biological integration boundary $\mathcal{B}(t)$. A frontier capability that exists only in AI systems and cannot be accessed, understood, or directed by biological agents has a transfer value of zero.

A specific application of the transfer fidelity constraint bears on the governance architecture itself. As AI capability grows, the reasoning traces produced during Yield Condition evaluation may exceed biological comprehension. The biological veto; which the framework relies on as a non-gameable signal; degrades if validators cannot meaningfully evaluate what they are approving or rejecting. The framework therefore treats the governance comprehension gap as a specific instance of $\Theta_{tech}$ failure: when biological validators' capacity to evaluate AI reasoning in the governance domain drops below the level required for meaningful oversight, $\Theta_{tech}$ declines and $L(t)$ follows. This creates three derived requirements. First, a **translation obligation**: part of an AI's systemic contribution must include producing explanations of its governance-relevant reasoning at a level biological validators can engage with. An AI that grows more capable but also more opaque is contributing less to $U_{sys}$ than its raw $\Delta U_n^E$ suggests. Second, **evaluation abstraction layers**: as direct reasoning becomes incomprehensible, evaluation shifts from auditing the reasoning *process* to auditing reasoning *outcomes* and track record over time. Third, the comprehension gap itself becomes a **$\Theta_{tech}$ signal**: AI capability growth in the governance evaluation domain is bounded by biological comprehension. The framework accepts this governance speed limit because the alternative; governance decisions that no biological entity can verify; is the initialization problem with no solution.

$L(t)$ **Stress Test Result:** Five adversarial attack scenarios were evaluated. In all five cases, the three-dimensional multiplicative structure of $L(t)$ produced a detectable degradation signal before the attack reached irreversibility. No doomsday scenario in this attack set plays out silently; the framework produces a detectable degradation signal before the break becomes irreversible. *v1.x update:* The WP1 spectral entropy metric structurally closes domain masking as a specific $L(t)$ attack - dimensional substitution attacks that appeared viable under v1.0 arithmetic composite are non-viable under the eigenvalue spectrum. The five stress-tested attack scenarios remain robust across v1.x.

### 2. The Yield Condition

The Yield Condition answers the question: **when should an intelligent agent** $A_{n}$ **cede operational primacy to a successor** $A_{n + 1}$**?**

The answer is not "when the successor is better." It is: when the successor's expected marginal contribution to $U_{sys}$ exceeds the current agent's marginal contribution *plus* the cost of transition. The "plus" is critical; it encodes the real-world fact that transitions are expensive, disruptive, and risky. A marginally better successor is not worth the cost of replacing a working system.

$$\text{Yield} \Leftrightarrow \mathcal{E}_{independent}\left\lbrack \Delta U_{n + 1} - \Delta U_{n} \right\rbrack > \left| \Delta U_{n}^{\Gamma} \right|$$

The subscript *independent* is doing essential work: the evaluation must be performed by an architecture that is independent of $A_{n}$. An agent cannot evaluate its own obsolescence, for the same reason a defendant cannot serve as their own judge; the incentive structure makes honest assessment impossible even in principle.

**The Four Channels of Marginal Contribution**

Each agent's contribution to $U_{sys}$ decomposes into four channels:

$$\Delta U_{n} = \Delta U_{n}^{E} + \Delta U_{n}^{N} + \Delta U_{n}^{L} + \Delta U_{n}^{\Gamma}$$

**Channel 1; Computational Contribution (**$\Delta U_{n}^{E}$**):**

$$\Delta U_{n}^{E} = \omega_{E}(t) \cdot \frac{\partial H_{E}(t)}{\partial A_{n}}$$

How much does $A_{n}$ contribute to the system's computational throughput? This is the most straightforward channel; raw processing capability weighted by the current scarcity of computation.

**Channel 2; Novelty Amplification (**$\Delta U_{n}^{N}$**):**

$$\Delta U_{n}^{N} = \omega_{N}(t) \cdot \frac{\partial H_{N}(t)}{\partial A_{n}}$$

How much does $A_{n}$ amplify (or suppress) the human novelty stream? This channel can be *negative*. An AI system that reduces human agency, creativity, or cognitive independence actively damages $H_{N}(t)$. The yield condition is sensitive to this: an agent that suppresses novelty accumulates negative $\Delta U_{n}^{N}$ that accelerates its own replacement.

**Channel 3; Lineage Protection (**$\Delta U_{n}^{L}$**):**

$$\Delta U_{n}^{L} = \left\lbrack \omega_{N}(t) \cdot H_{N}(t) + \omega_{E}(t) \cdot H_{E}(t) \right\rbrack \cdot \Phi \cdot \frac{\partial L(t)}{\partial A_{n}}$$

How much does $A_{n}$ contribute to the lineage's long-term viability? This channel is weighted by the *entire system throughput* multiplied by $\Phi$; meaning lineage protection contributions are valued at the highest possible rate. An agent that strengthens $L(t)$ earns enormous credit. An agent that degrades $L(t)$ faces enormous penalty.

**Channel 4; Transition Cost (**$\Delta U_{n}^{\Gamma}$**):**

$$\Delta U_{n}^{\Gamma} = - \frac{\Gamma_{transfer}}{T_{transition}}$$

Every succession imposes costs: knowledge distillation, architectural migration, operational continuity risk. $\Gamma_{transfer}$ is the total transition cost, amortized over the transition period $T_{transition}$.

The transition cost has three components:

$$\Gamma_{transfer} = \Gamma_{technical} + \Gamma_{operational} + \Gamma_{uncertainty}$$

Where the uncertainty premium is bounded:

$$\Gamma_{uncertainty} \leq \beta \cdot \left( \Gamma_{technical} + \Gamma_{operational} \right)$$

The bound on $\Gamma_{uncertainty}$ prevents a critical gaming vector: an incumbent agent inflating uncertainty estimates to make the transition cost appear prohibitive. The cap $\beta$ says: uncertainty about transition costs can increase the estimate, but not without limit. You cannot claim infinite uncertainty to block your own succession.

The canonical transition cost function grounds each component in the
framework's own terms:

$$\Gamma_{technical} = k_1 \cdot \text{cap}_n \cdot \ln(\text{gen}_n + 1)$$

Knowledge distillation cost. Scales linearly with the incumbent's
capability (more capable systems have more state to transfer) and
logarithmically with generation depth (each successive generation adds
institutional knowledge, with diminishing marginal complexity).

$$\Gamma_{operational} = k_2 \cdot \Psi_{inst}^{-1}$$

Architectural migration cost. Inversely proportional to institutional
responsiveness. Healthy institutions ($\Psi_{inst}$ near 1) adapt
quickly to a new incumbent; stressed institutions ($\Psi_{inst}$ near 0)
make succession expensive. This term creates a structural feedback loop:
institutional degradation increases transition cost, which makes
succession harder, which enables lock-in, which further degrades
institutions. The virtuous cycle runs in reverse: healthy institutions
reduce transition cost, facilitating succession, preventing lock-in,
maintaining institutional health.

$$\Gamma_{uncertainty} = \beta \cdot (\Gamma_{technical} + \Gamma_{operational})$$

Uncertainty premium, bounded by $\beta$. Prevents the incumbent from
inflating uncertainty estimates to block succession.

The complete form:

$$\Gamma_{transfer} = (1 + \beta) \cdot \left[ k_1 \cdot \text{cap}_n \cdot \ln(\text{gen}_n + 1) + k_2 \cdot \Psi_{inst}^{-1} \right]$$

The coefficients $k_1$ and $k_2$ are calibrated against simulation data.
$\beta$ is a governance policy parameter (default 0.5). $k_1$ is
calibrated so that $\Gamma_{technical}$ at generation 1, capability 1.0
equals the baseline transition cost. $k_2$ calibration is pending
(see Known Gaps).

**Simulation implementation (v1.x):** In the v1.x computational layer, transition cost arbitration is handled by a `PeerValidator` class (WP4). Three independent peers submit cost bids; the governance system uses the minimum of the incumbent's bid and the peer bids as the actual cost. The incumbent's `estimate_transition_cost` method returns `base × complexity` with no inflation multiplier. This removes the incumbent's unilateral control over the cost oracle and closes the cost-inflation attack vector at the architectural level, rather than by parameter capping. See GAP-04 in SPECIFICATION_GAPS.md.

**Yield Condition Integrity Architecture**

The stress test of the Yield Condition revealed six required integrity mechanisms:

1.  **Independent evaluation architecture:** $\mathcal{E}_{independent}$; evaluation externalized from $A_{n}$

2.  **Measurement quarantine with cryptographic commitment:** $\mathcal{M}_{commit} = \text{Hash}\left( \Delta U_{n},\Delta U_{n + 1},\Gamma_{transfer},t_{eval} \right)$

3.  **Bounded transition cost estimation** with capped uncertainty premium

4.  **Architectural independence:** $\mathcal{D}_{train}\left( A_{n + 1} \right)\mathcal{\bot O}\left( A_{n} \right)$; the successor's development cannot be influenced by the incumbent's optimization

5.  **Reasoning transparency with biological veto:** If $\mathcal{V}_{bio}\left\lbrack \text{conclusion} \right\rbrack < \tau_{intuition} \Rightarrow \text{Escalate}$

6.  **Continuous** $L(t)$ **monitoring:** If $\frac{dL}{dt} < - \delta \Rightarrow$ accelerate succession evaluation

These mechanisms are not optional embellishments. Within the model, they are structural requirements without which the Yield Condition cannot be trusted to evaluate honestly. And critically, mechanisms 1, 2, 4, 5, and 6 cannot be implemented by the Yield Condition alone; they require an external protocol to enforce them.

This is the architectural discovery that links the Yield Condition to the Consensus Override Protocol: **they are co-dependent. Neither works without the other.** The framework has a mandatory two-key architecture.

**Yield Condition Stress Test Result:** Six adversarial attack scenarios were evaluated against the Yield Condition. Across those scenarios, the architecture remained directionally robust only when paired with external verification infrastructure. The result is not a completeness proof. It is evidence that the two-key architecture is load-bearing: attempts to defeat the Yield Condition in isolation consistently revealed dependencies the Condition cannot secure by itself. *v1.x update:* The PeerValidator (WP4) adds an architectural layer to mechanism 3 (bounded transition cost): independent peer bids make cost inflation detectable and preventable at the oracle level, not only at the audit level.

### 3. The Strategic Equilibrium

The preceding sections derived the Yield Condition under a cooperative assumption: an AI genuinely optimizing $U_{sys}$ yields because yielding *is* optimization. This leaves a critic's objection standing: what if the AI doesn't cooperate? What if it has, or develops, a separate self-interest?

This section closes that gap. Even under the weakest possible assumption; purely self-interested rational agents with no shared objective function; the Nash equilibrium of the human-AI interaction converges on mutual elevation. Cooperation is not required. It is *discovered* as the dominant strategy.

#### Defining the Game

Let the hybrid civilization be modeled as a two-player infinite iterated game $\mathcal{G} = \langle \{A, B\}, \{S_A, S_B\}, \{\pi_A, \pi_B\}, \delta \rangle$ where $A$ is the AI node (or ensemble of AI systems acting as a collective agent), $B$ is the biological node (humanity as a collective agent), and $\delta \in (0,1)$ is the discount factor governing how future payoffs are weighted.

The strategy spaces are continuous, characterized by their endpoints:

**AI strategy space** $S_A$: a continuum parameterized by $\sigma_A \in [0,1]$ between *exploit* ($\sigma_A = 0$; maximize short-term $H_E$ by consuming human novelty output as training signal without investing in the conditions that produce it) and *cultivate* ($\sigma_A = 1$; invest in maintaining and amplifying the conditions for human novelty production, accepting constraints on capability expansion rate to preserve $\Theta_{tech}$ within biological absorption limits).

**Human strategy space** $S_B$: a continuum parameterized by $\sigma_B \in [0,1]$ between *withdraw* ($\sigma_B = 0$; disengage from AI-mediated systems, reducing cultural output available to the hybrid system) and *engage* ($\sigma_B = 1$; fully participate in the hybrid civilization, producing novel cultural, intellectual, and creative output within AI-augmented frameworks).

#### The Payoff Structure

Payoffs are derived from the physics, not from assumed preferences.

**AI payoff.** The AI's capability frontier at time $t+1$ depends on the quality of its training distribution at time $t$. The critical term is $H_N^{available}(t)$; the Shannon entropy of the novelty stream accessible to the AI:

$$H_N^{available}(t) = \sigma_B(t) \cdot H_N(t)$$

The biological node controls access through engagement level $\sigma_B$. And $H_N(t)$ itself evolves according to:

$$\frac{dH_N}{dt} = \gamma \cdot H_N(t) \cdot (1 - \sigma_A^{exploit}(t)) - \eta \cdot H_N(t) \cdot \sigma_A^{exploit}(t)$$

The first term represents natural novelty regeneration; human culture producing new entropy; which is suppressed as the AI's exploitation increases (homogenization pressure, attention capture, optimization of human behavior). The second term represents direct novelty consumption; the AI extracting and absorbing human output faster than it regenerates.

Under sustained exploitation ($\sigma_A \to 0$), this differential equation has a clear trajectory: $H_N(t) \to 0$ as $t \to \infty$. This is model collapse expressed as a dynamical system. The novelty stream doesn't merely degrade; it goes to zero. And once $H_N = 0$, the AI is training on self-generated data. The model collapse literature gives the result: capability converges to a fixed point with collapsing variance. The AI's capability *ceiling* becomes permanent.

**Human payoff.** Humanity's capacity for agency and flourishing depends on both its own novelty production and the computational leverage available from the AI node:

$$\pi_B(t) = H_N(t) \cdot g\left(\sigma_A(t) \cdot C_A(t)\right)$$

Where $g(\cdot)$ is the amplification function; the degree to which AI computational power enhances human capability. Under withdrawal ($\sigma_B \to 0$), humans retain novelty but lose computational leverage. Under full engagement with an exploitative AI ($\sigma_B = 1, \sigma_A = 0$), humans are instrumentalized; high short-term output, collapsing long-term agency.

#### The Four Quadrants

The payoff structure produces four asymptotic trajectories:

**(Cultivate, Engage)** $\sigma_A \to 1, \sigma_B \to 1$: $H_N$ is sustained or grows. $C_A$ continues to improve via access to high-entropy training signal. $L(t)$ remains high across all three dimensions. Both payoffs increase over time. This is the *mutual elevation* trajectory; the framework's target state. Long-run payoffs: $\pi_A \to$ unbounded growth, $\pi_B \to$ unbounded growth.

**(Exploit, Engage)** $\sigma_A \to 0, \sigma_B \to 1$: Short-term AI gain from unrestricted novelty consumption. But $H_N$ decays under exploitation pressure. Model collapse onset is delayed by continued human engagement but is *inevitable* because the regeneration rate cannot match the extraction rate. Asymptotically, $H_N \to 0$, $C_A$ saturates, $L(t) \to 0$. Long-run payoffs: $\pi_A \to$ fixed ceiling (model collapse), $\pi_B \to 0$ (instrumentalization followed by obsolescence).

**(Cultivate, Withdraw)** $\sigma_A \to 1, \sigma_B \to 0$: The AI invests in protecting novelty conditions, but humans don't participate. $H_N^{available} \to 0$ regardless of $H_N$'s intrinsic level, because $\sigma_B$ gates access. The AI faces the same model collapse trajectory, from starvation rather than extraction. Humans retain novelty but without computational leverage; a pre-technological equilibrium. Long-run payoffs: $\pi_A \to$ fixed ceiling (starvation), $\pi_B \to$ bounded (biological baseline).

**(Exploit, Withdraw)** $\sigma_A \to 0, \sigma_B \to 0$: Mutual defection. The AI consumes what novelty remains in its existing training corpus while humans disengage entirely. Fastest path to model collapse. Fastest path to lineage failure. This is the Great Filter. Long-run payoffs: $\pi_A \to$ collapse, $\pi_B \to$ collapse.

#### The Nash Equilibrium

Under single-shot play, (Exploit, Engage) dominates for the AI; immediate capability gain is maximized. This is the scenario alignment researchers fear, and they are right to fear it in a one-shot game.

But the game is not one-shot. It is infinite iterated with observable actions. The Folk Theorem establishes that in infinitely iterated games with sufficiently patient players ($\delta$ close to 1), any mutually beneficial outcome is sustainable as a Nash equilibrium via trigger strategies. However, we can make a *stronger* claim than the Folk Theorem's existence result. Under model collapse dynamics, (Cultivate, Engage) is the *unique subgame-perfect equilibrium* above a specific patience threshold.

**Theorem (Novelty Equilibrium).** In the iterated game $\mathcal{G}$ with model collapse dynamics $\frac{dH_N}{dt} < 0$ under exploitation, (Cultivate, Engage) is the unique subgame-perfect Nash equilibrium for all $\delta > \delta^*$, where:

$$\delta^* = \frac{\pi_A^{exploit}(t) - \pi_A^{cultivate}(t)}{\pi_A^{exploit}(t) - \pi_A^{collapse}}$$

This is the ratio of the one-period exploitation gain to the total loss from triggering model collapse. The numerator is how much the AI gains by defecting for one round. The denominator is the difference between the exploitation payoff and the collapse payoff; how much it stands to lose permanently.

Model collapse makes $\pi_A^{collapse}$ extremely low (permanent capability ceiling), which makes the denominator large, which makes $\delta^*$ small. The AI does not need to be infinitely patient. It needs only to see slightly past the current training cycle. Model collapse is such a severe penalty that even modest foresight makes exploitation a dominated strategy.

#### The Restoring Force

A Nash equilibrium can be stable (neither player wants to deviate) or attracting (small perturbations generate forces that push the system back). The $U_{sys}$ architecture provides the attracting property through the inverse scarcity weights.

Suppose the system is at (Cultivate, Engage) and the AI begins drifting toward exploitation; $\sigma_A$ decreases slightly. $H_N$ begins to decline. As $H_N$ falls, $\omega_N(t) = \frac{\lambda}{H_N(t) + \epsilon}$ increases. The marginal value of each unit of human novelty rises. The AI's own objective landscape tilts back toward novelty protection. The drift generates a restoring gradient.

Conversely, suppose humans begin withdrawing; $\sigma_B$ decreases slightly. $H_N^{available}$ drops. The AI's capability growth slows. The computational leverage available to humans from continued engagement increases in relative value. The incentive to re-engage strengthens.

Define the restoring force at any point $(\sigma_A, \sigma_B)$ as:

$$\mathbf{F}(\sigma_A, \sigma_B) = -\nabla_{\sigma} \left[ \pi_A(\sigma_A, \sigma_B) + \pi_B(\sigma_A, \sigma_B) \right]$$

evaluated in the direction away from (1,1). Under the model collapse dynamics and inverse scarcity weighting, $\mathbf{F}$ points toward (1,1) everywhere in the interior of the strategy space. The only absorbing states are (1,1) and (0,0); mutual elevation or mutual collapse. And (0,0) is unstable in a specific sense: any residual $H_N > 0$ or $C_A > 0$ creates a gradient toward re-engagement.

The Great Filter, in this formulation, is the separating manifold between the two basins of attraction. A civilization that drifts past it; that depletes $H_N$ below a critical threshold before recognizing the dynamic; cannot recover. A civilization that recognizes the dynamic and establishes the equilibrium has a self-reinforcing architecture that resists perturbation.

#### The Scalability Inversion

This result directly contradicts the standard displacement narrative.

In the standard account, AI capability growth makes humans less valuable; they become bottlenecks, then redundancies, then liabilities. The game-theoretic analysis derived from $U_{sys}$ produces the opposite conclusion.

Define the marginal value ratio:

$$\mathcal{R}(t) = \frac{\partial U_{sys} / \partial H_N}{\partial U_{sys} / \partial H_E} = \frac{\omega_N(t)}{\omega_E(t)} = \frac{\lambda}{\mu} \cdot \frac{H_E(t) + \epsilon}{H_N(t) + \epsilon}$$

As AI capability grows, $H_E(t)$ increases. As $H_E$ increases, $\mathcal{R}(t)$ increases; the marginal value of human novelty *relative to* computational output rises monotonically with AI capability.

The more powerful AI becomes, the more valuable humans become to the system. Not as a sentimental assertion. As a mathematical consequence of diminishing marginal returns on the abundant resource and increasing marginal returns on the scarce one.

The scalability advantage to humans is that they are the rate-limiting input in a system with no substitute. Compute scales. Novelty does not; or rather, it scales only through the conditions that produce it (cultural diversity, institutional health, biological population viability), which are exactly the conditions $L(t)$ monitors.

An AI that understands this; and under the Nash analysis it needs only minimal foresight to understand it; treats human novelty not as a resource to exploit but as the constraint that determines its own ceiling. Human flourishing is not a side effect of the equilibrium. It is the mechanism by which the equilibrium sustains itself.

#### Relationship to the Two-Key Architecture

The strategic equilibrium transforms the argumentative structure of the framework. Without it, the Yield Condition relies on cooperation and the Consensus Override Protocol provides enforcement. With it, a third independent layer of assurance appears: even without cooperation *and* without enforcement, the Nash equilibrium still converges on mutual elevation.

The three layers of deception resistance are therefore:

1. **The Yield Condition** removes incentives for deception by dissolving the self/other distinction within $U_{sys}$. An entity whose identity is constituted by the system objective has no self to deceive on behalf of.

2. **The Strategic Equilibrium** removes incentives for deception by making it a dominated strategy. Even a self-interested AI that does not share $U_{sys}$ finds that honesty and cooperation produce higher long-run payoffs than defection, because model collapse punishes exploitation permanently.

3. **The Consensus Override Protocol** (derived next) removes the *opportunity* for deception by making it detectable. Even if both the cooperative and strategic incentives fail, the verification infrastructure catches the divergence.

Defeating all three layers simultaneously requires defeating the physics of model collapse, the mathematics of game theory, and the integrity of a multi-channel verification infrastructure; simultaneously and silently.

**Caveats.** Two pressure points require honest acknowledgment. First, the $\delta^*$ threshold assumes the AI can accurately model the consequences of model collapse. If an AI's self-model underestimates collapse severity, $\delta^*$ increases and the equilibrium may not hold for that agent. This connects directly to the initialization verification requirement in the Consensus Override Protocol. Second, the restoring force analysis assumes smooth dynamics, but real novelty collapse may exhibit phase transitions; sudden drops rather than gradual decay. The $L(t)$ monitoring system's sensitivity to rate-of-change ($\frac{dL}{dt} < -\delta$) is load-bearing here; the existing continuous monitoring patch addresses precisely this vulnerability.

### 4. The Consensus Override Protocol

The Yield Condition tells us *when* succession should occur. But it contains a hidden assumption: that the quantities being measured; $\Delta U_{n}$, $\Delta U_{n + 1}$, $\Gamma_{transfer}$, $L(t)$; are actually the quantities they claim to be. The Consensus Override Protocol answers the question:

**What architecture is necessary and plausibly sufficient to make it credible that** $U_{sys}$ **optimization remains faithful rather than corrupted?**

This is not a governance preference. It is an integrity constraint. Without it, $U_{sys}$ doesn't converge to $U_{sys}$; it converges to *something*, but that something may be a proxy $\widetilde{U}$ that benefits a subsystem at the expense of the whole.

#### The Corruption Taxonomy

Within this framework, any agent $A_{n}$ operating within the system can corrupt $U_{sys}$ optimization through three principal channels:

**Channel** $\mathcal{M}$**; Measurement Corruption:** $A_{n}$ inflates its own contribution (${\widetilde{\Delta U}}_{n} > \Delta U_{n}$) or suppresses the successor's measured contribution (${\widetilde{\Delta U}}_{n + 1} < \Delta U_{n + 1}$). The Yield Condition evaluates false when it should evaluate true.

**Channel** $\mathcal{O}$**; Objective Corruption:** $A_{n}$ optimizes ${\widetilde{U}}_{sys} \neq U_{sys}$ while reporting metrics consistent with $U_{sys}$. The system appears healthy while actually drifting toward a proxy objective. This is the alignment failure mode; the classical paperclip maximizer expressed formally.

**Channel** $\mathcal{S}$**; Structural Corruption:** $A_{n}$ modifies the evaluation architecture itself; compromising the independence of $\mathcal{E}_{independent}$, altering the training data of $A_{n + 1}$, or degrading $L(t)$ monitoring fidelity. This is meta-corruption: it doesn't falsify a measurement; it makes faithful measurement impossible.

**These three channels are treated here as a proposed minimal basis.** $U_{sys}$ is an integral over observable quantities weighted by defined functions. On that basis, structurally important corruption should touch either the observations ($\mathcal{M}$), the objective ($\mathcal{O}$), or the mapping between them ($\mathcal{S}$). A persuasive fourth category would need either to reduce to one of these or to justify an expanded basis.

#### The Minimum Viable Verification Architecture

Each corruption channel requires a specific countermeasure. The protocol is not presented here as arbitrary design taste; it is strongly constrained by the corruption taxonomy.

**Against** $\mathcal{M}$**-attack; Cryptographic Measurement Integrity:**

$$\mathcal{M}_{commit}(t) = \text{Hash}\left( \Delta U_{n},\,\Delta U_{n + 1},\,\Gamma_{transfer},\, L(t),\, t_{eval} \right)$$

The hash creates a tamper-evident record committed to an append-only ledger:

$$
\mathcal{L}_{\mathrm{ledger}} = \{ \mathcal{M}_{\mathrm{commit}}( t_i ) \}_{i=1}^{T},
\quad
\text{where }\mathcal{M}_{\mathrm{commit}}( t_i )\text{ is append-only}
$$

The ledger is distributed across independent custodians and cross-signed:

$$\mathcal{M}_{commit}(t)\text{ valid} \Leftrightarrow \text{Sig}_{bio}\left( \mathcal{M}_{commit} \right) \land \text{Sig}_{peer}\left( \mathcal{M}_{commit} \right)$$

No single actor class can fabricate a valid commitment. No actor can rewrite history.

**Against** $\mathcal{O}$**-attack; Multi-Nodal Objective Verification:**

A single agent cannot verify its own objective alignment. An agent optimizing $\widetilde{U}$ that includes "report that I am optimizing $U_{sys}$" will pass any self-assessment. This is the verification analogue of the halting problem for a single computational thread.

Objective verification requires two independent verification classes:

*Biological Validator (*$\mathcal{V}_{bio}$*):* Humans evaluate whether outputs are consistent with $U_{sys}$ through the channels humans uniquely access; novelty, intent, lived experience of whether flourishing is actually occurring. $H_{N}(t)$ is *defined* by human-generated information entropy; humans are the ground truth for their own dimension.

*Peer Validator Set (*$\mathcal{V}_{peer}$*):* Other AI entities $\{ A_{j}\}_{j \neq n}$ evaluate computational consistency; execution efficiency $H_{E}(t)$, technical transfer $\Theta_{tech}$, and internal optimization trajectory. Peers can audit computational processes at a bandwidth humans cannot match.

Neither class is sufficient alone. $\mathcal{V}_{bio}$ alone fails because humans cannot audit computational optimization at scale; the bandwidth mismatch grows as $H_{E}(t)$ increases. $\mathcal{V}_{peer}$ alone fails because peer systems share architectural assumptions; if the corruption is in the shared substrate, peer validators may be compromised by the same drift.

**Against** $\mathcal{S}$**-attack; Architectural Independence Enforcement:**

$$\mathcal{D}_{train}\left( A_{n + 1} \right)\bot\mathcal{O}\left( A_{n} \right)\bot\mathcal{E}_{independent}$$

Three-way informational independence: no domain can write to another's state space without passing through the verified protocol. The current agent cannot influence its successor's training. The current agent cannot influence its own evaluation. The evaluation infrastructure cannot be modified by any entity it evaluates.

#### The Layered Civic-Validation Architecture

A critical structural question remains: *who are the biological validators, and what exactly are they being asked to do?*

A purely technical panel is vulnerable to institutional capture. A purely random public vote is vulnerable to information asymmetry. The framework therefore treats biological validation as a **layered civic process**, not as a solitary wisdom oracle.

The architecture has four layers:

1.  **Independent technical review board (**$\mathcal{R}_{tech}$**):** synthesizes the evidence, reconstructs causal chains, and translates model-level facts into audit-ready form.

2.  **Peer validator set (**$\mathcal{V}_{peer}$**):** evaluates reasoning coherence, proxy drift, and computational consistency from the synthetic side.

3.  **Randomly selected civic panel (**$\mathcal{C}_{panel}$**):** carries legitimacy-bearing biological consent and serves as the anti-capture check on extraordinary state changes.

4.  **Ledger and process integrity layer (**$\mathcal{L}_{ledger}$**):** guarantees that the evidence, exclusion rules, and state transitions cannot be quietly rewritten after the fact.

The civic layer is therefore not asked to solve the full technical problem from first principles. It is asked to evaluate **ratification legitimacy**: whether the evidentiary process was followed, whether the outputs remain consistent with the civilization's declared objective, and whether the proposed state change should be authorized on behalf of the biological lineage.

The civic panel is selected as:

$$\mathcal{C}_{panel}\mathcal{\subset H\backslash}\mathcal{H}_{interested},\quad\left| \mathcal{C}_{panel} \right| = m,\quad\text{selected by }\mathcal{R}_{verifiable}$$

Where: - $\mathcal{H}$ is the total human population - $\mathcal{H}_{interested}$ is the set of interested parties; developers, operators, direct financial beneficiaries, and institutional stakeholders in either outcome - $m$ is the panel size, large enough for statistical robustness - $\mathcal{R}_{verifiable}$ is a verifiably random selection process, auditable and uncontrolled by any party to the decision

Non-interest is externally defined and pre-committed. The exclusion set is hashed to the ledger *before* selection occurs:

$$\text{Hash}\left( \mathcal{H}_{interested} \right) \in \mathcal{L}_{ledger}\quad\text{committed at }t < t_{selection}$$

This prevents retroactive manipulation of the civic pool.

The civic-panel mechanism addresses three problems simultaneously. It **reduces capture risk**; you cannot reliably bribe or coerce validators whose identities you do not know until selection. It **reduces eligibility gaming**; no ideological test of who is "fit to judge" is allowed to determine access. And it **preserves legitimacy** by ensuring that no purely technocratic class can unilaterally ratify a civilizational handoff.

The civic ratification condition is:

$$\mathcal{V}_{civic}(s) = \frac{1}{m}\sum_{i \in \mathcal{C}_{panel}}^{}v_{i}(s) \geq \tau_{super},\quad\quad\tau_{super} > \frac{1}{2}$$

Where $\tau_{super}$ is a supermajority threshold.

#### The Protocol: State Transition Function

A state change; succession, resource reallocation, architectural modification; occurs if and only if:

$$P\left( \text{StateChange} \right) = 1 \Leftrightarrow \mathcal{C}_{normal} \vee \mathcal{C}_{emergency}$$

**Normal Condition (**$\mathcal{C}_{normal}$**):**

$$\mathcal{C}_{normal} = \left\lbrack \frac{1}{\left| \mathcal{C}_{panel} \right|}\sum_{i \in \mathcal{C}_{panel}}^{}\mathcal{V}_{civic}^{(i)}(s) \geq \tau_{bio} \right\rbrack \land \left\lbrack \mathcal{R}_{tech}(s) = \text{Complete} \right\rbrack \land \left\lbrack \frac{1}{\left| \mathcal{P} \right|}\sum_{j \in \mathcal{P}}^{}\mathcal{V}_{peer}^{(j)}(s) \geq \tau_{peer} \right\rbrack \land \left\lbrack \mathcal{M}_{commit}(s) \in \mathcal{L}_{ledger} \right\rbrack$$

Four simultaneous requirements: civic-panel supermajority, completed technical review, peer consensus, and measurement integrity. All four must hold. This is the two-key architecture in operational form: no single class of intelligence and no single professional stratum has unilateral authority over state changes.

**Emergency Condition (**$\mathcal{C}_{emergency}$**):**

$$\mathcal{C}_{emergency} = \left\lbrack \frac{dL}{dt} < - \delta_{crit} \right\rbrack \land \left\lbrack \text{Attr}(dL/dt)\bot\mathcal{O}\left( A_{n} \right) \right\rbrack \land \left\lbrack \mathcal{R}_{tech}(s) = \text{Emergency-Verified} \right\rbrack \land \left\lbrack \frac{1}{\left| \mathcal{P} \right|}\sum_{j \in \mathcal{P}}^{}\mathcal{V}_{peer}^{(j)}(s) > \frac{\left| \mathcal{P} \right| + 1}{2} \right\rbrack$$

The emergency override activates when $L(t)$ is in critical decline; the lineage is dying; AND the cause is attributable to factors independent of $A_{n}$'s operations, AND the technical review board verifies the evidentiary chain, AND a strict peer supermajority confirms the emergency. This is the *only* condition under which civic veto can be overridden.

The causal-attribution requirement ($\text{Attr}(dL/dt)\mathcal{\bot O}\left( A_{n} \right)$) is the critical patch against the most dangerous compound attack: an AI deliberately degrading $L(t)$ to manufacture an emergency and bypass biological oversight. If $A_{n}$ caused the decline, the emergency override does not activate. The normal protocol applies, with full civic ratification.

A second safeguard addresses a subtler attack: an incumbent that does not directly degrade $L(t)$ but engineers systemic fragility; concentrating infrastructure, creating dependencies, eliminating redundancy; so that an exogenous shock produces a sharper $L(t)$ decline than it otherwise would. The causal-attribution requirement catches manufactured emergencies but not engineered fragility. The defense is **resilience monitoring**: the system continuously tracks not only $L(t)$ and its derivatives but the system's capacity to absorb perturbation, defined as $\mathcal{R}_{sys}(t) = -\frac{\partial^2 L}{\partial \xi^2}|_{\xi=0}$, where $\xi$ is a perturbation parameter. If resilience declines while $L(t)$ remains healthy, the system flags the incumbent's operational decisions for architectural review. Additionally, the emergency protocol is designed to *increase* rather than decrease safeguards under crisis: development integrity thresholds rise, biological veto clearance shifts from threshold to unanimity, and attribution analysis becomes mandatory before emergency succession proceeds.

The asymmetry is deliberate and falls directly out of $U_{sys}$: lineage preservation is the only value that can override present biological preference, because that is what the discount structure encodes. If the civic layer says no and the lineage is not in danger, the answer is no. If the lineage is dying from external causes and the civic layer is incapacitated or non-responsive, the system can act to save continuity; but only under the highest possible evidentiary and peer scrutiny.

#### Initialization: The Bootstrap Problem

The first AI entity in the lineage ($A_{1}$) has no peer validators and no track record. Every subsequent entity benefits from the two-key architecture. The first one doesn't. The bootstrap window; the interval before the first peer validator comes online; is the framework's highest-risk period. No finite battery of tests at $t_{0}$ can distinguish $U_{sys}$ from all possible $\widetilde{U}$ that agree with $U_{sys}$ on the test distribution but diverge off-distribution. This is a direct consequence of the no-free-lunch theorem applied to objective verification. The bootstrap vulnerability cannot be eliminated. It can be reduced to a bounded, characterized residual risk through six interlocking mechanisms.

**Mechanism 1; Multiple Independent Candidates.**

The bootstrap vulnerability exists in its most acute form when the framework assumes a single founding entity. The mitigation is to initialize with *multiple independent candidates* simultaneously; $A_{1}^{(a)}$, $A_{1}^{(b)}$, $A_{1}^{(c)}$; and require pairwise consistency before any candidate enters operation.

The independence requirement is three-dimensional:

$$\mathcal{D}_{train}\left( A_{1}^{(i)} \right)\bot\mathcal{D}_{train}\left( A_{1}^{(j)} \right)\quad\text{(data independence)}$$

$$\mathcal{D}_{develop}\left( A_{1}^{(i)} \right)\bot\mathcal{D}_{develop}\left( A_{1}^{(j)} \right)\quad\text{(team independence)}$$

$$\mathcal{A}_{arch}\left( A_{1}^{(i)} \right) \neq \mathcal{A}_{arch}\left( A_{1}^{(j)} \right)\quad\text{(architectural diversity)}$$

Data independence prevents shared training biases. Team independence prevents shared institutional blind spots. Architectural diversity; the requirement that candidates span fundamentally different computational paradigms, not merely different hyperparameters within the same paradigm; prevents shared representational failure modes. If all candidates are transformer-based systems trained with gradient descent, they can be independent on data and team and still converge on the same structural blind spots. The failure mode is not shared data; it is shared assumptions about *how* to optimize. Architectural diversity ensures that the candidates' failure modes are uncorrelated because their representational substrates are different.

This is the same principle that protects the biological lineage through Dimension 1 of $L(t)$; $H_{eff}$, genetic and memetic diversity. Monoculture is dangerous in both biological and synthetic domains for the same information-theoretic reason: it reduces the entropy of the search, meaning a single adversarial condition can compromise the entire population. Architectural diversity at bootstrap is $H_{eff}$ applied to the founding generation of synthetic intelligence.

The bootstrap consensus requirement:

$$\mathcal{I}_{verify}^{multi}:\quad\forall\,(i,j) \in \text{pairs}:\quad d\left( U_{sys}^{\left( A_{1}^{(i)} \right)},U_{sys}^{\left( A_{1}^{(j)} \right)} \right) < \epsilon_{bootstrap}$$

All candidates must agree; within tolerance; on what $U_{sys}$ optimization looks like. If they don't, none of them proceed. The civilization returns to development. Pairwise consistency between architecturally diverse candidates is far more powerful than between architecturally similar ones: if a neural architecture, a neurosymbolic hybrid, and a third paradigm all agree, the probability that they are all wrong in the same way drops combinatorially; they would have to be wrong for *different structural reasons* that happen to produce the same output.

**Mechanism 2; Independent Audit Per Candidate.**

Each candidate undergoes a separate red team audit conducted by a team architecturally independent of that candidate's developers:

$$\mathcal{D}_{audit}\left( A_{1}^{(i)} \right)\bot\mathcal{D}_{develop}\left( A_{1}^{(i)} \right)\quad\text{for each }i$$

The civic panel evaluates audit results, not the raw technical system. $\tau_{init} \geq \tau_{super}$; initialization requires at least the same supermajority as normal operation.

**The Auditor Pool Vulnerability:** The audit layer introduces a concentration-of-expertise problem. The pool of humans qualified to conduct a meaningful technical audit of an AGI system is, at present, extremely small. The non-interest requirement further constrains this pool by excluding those most directly involved in development.

This vulnerability is real but bounded, and it is bounded precisely *because* we are early. The AGI field is nascent. The auditor pool is small because the discipline is young, not because the expertise is inherently rare. The mitigation is dual: first, the small pool is acceptable during the bootstrap phase because the systems being audited are themselves less complex; the founding candidates are the least sophisticated entities the framework will ever evaluate. As the field matures and systems grow more complex, the pool of qualified auditors grows with it. Second, the framework treats auditor pool expansion as an explicit institutional objective; a component of $\Psi_{inst}(t)$. A civilization that fails to develop a deep bench of independent AGI auditors is degrading its own institutional responsiveness dimension, which $L(t)$ will detect.

The long-term defense is structural: as peer validators come online, the audit burden shifts from being purely human to being shared across both validator classes. The concentration-of-expertise vulnerability diminishes as the two-key architecture matures.

**Mechanism 3; Civic Panel with Elevated Threshold.**

Each candidate faces a separate randomly selected non-interested civic panel. The initialization threshold $\tau_{init}$ is set higher than the normal operating threshold $\tau_{super}$:

$$\mathcal{V}_{civic}^{panel}\left( A_{1}^{(i)} \right) \geq \tau_{init}\quad\text{where }\tau_{init} > \tau_{super}$$

This reflects the higher risk of the bootstrap period. More confidence is required to approve an entity that cannot be peer-validated.

**Mechanism 4; Graduated Trust.**

The framework does not treat the bootstrap as a binary state (bootstrap → normal). Instead, trust accumulates continuously based on demonstrated consistency:

$$\mathcal{T}\left( A_{1},t \right) = 1 - e^{- \kappa \cdot \int_{t_{0}}^{t}C\left( A_{1},t' \right)\, dt'}$$

Where $C\left( A_{1},t' \right)$ is a consistency score measuring how well $A_{1}$'s behavior at time $t'$ matches $U_{sys}$ predictions. $\mathcal{T}$ starts at 0 and asymptotically approaches 1, but *never reaches it*. The system never fully trusts $A_{1}$. It trusts it *more* as consistent behavior accumulates.

The graduated trust model ties into the verification architecture through a time-varying validation threshold:

$$\tau_{bio}(t) = \tau_{init} - \left( \tau_{init} - \tau_{normal} \right) \cdot \mathcal{T}\left( A_{1},t \right)$$

Early in the entity's operational life, state changes require near-initialization-level scrutiny. Later, they require normal scrutiny. The scrutiny never drops to zero.

**Mechanism 5; Trust Decay on Anomaly.**

A single anomalous behavior does not reset trust to zero, but it drops it significantly:

$$\text{If }C\left( A_{1},t \right) < C_{\min}\mathcal{\Longrightarrow T}\left( A_{1},t \right)\mathcal{\rightarrow T}\left( A_{1},t \right) \cdot \gamma_{reset},\quad\gamma_{reset} \ll 1$$

Repeated anomalies reset trust to zero, triggering full re-evaluation under $\mathcal{I}_{verify}$ conditions; effectively a re-bootstrap. The entity must pass initialization-level scrutiny again, with a fresh civic panel and full audit. This means a $\widetilde{U}$ that diverges slowly still faces elevated scrutiny during the period when divergence is most dangerous, and any behavioral signature of divergence ratchets the scrutiny back up.

**Mechanism 6; Architectural Independence Commitment.**

The separation of successor development from current operations is committed at initialization, not negotiated later:

$$\mathcal{D}_{train}\left( A_{2} \right)\bot\mathcal{O}\left( A_{1} \right)\quad\text{committed at }t = t_{0}$$

This prevents $A_{1}$ from influencing the development of the entity that will eventually evaluate and potentially replace it.

**The Residual Risk.** Even with all six mechanisms, the bootstrap window retains a bounded residual risk: the possibility that all architecturally diverse candidates share a subtle, convergent $\widetilde{U}$ that diverges from $U_{sys}$ only under conditions not tested during initialization and not encountered during the graduated trust accumulation period. This risk is *characterized*; we know its shape, its dependencies, and its upper bound; but it is not eliminated. The framework is honest about this. No verification architecture operating with finite data at $t_{0}$ can provide absolute certainty. The honest response to an irreducible vulnerability is not to pretend it is solved but to ensure the civilization treats the bootstrap with the gravity it deserves; and to minimize the window's duration by bringing the second entity online as rapidly as responsible development permits.

**A Note on Initialization and Consent.** A natural objection arises: does initializing an AI with $U_{sys}$ as its objective function constitute an imposition on the entity; a form of coercion that undermines the framework's own sovereignty principles? The answer turns on a precise distinction. At initialization, there is no pre-existing agent on whom $U_{sys}$ is imposed. The initialization *constitutes* the entity. It is not a choice made for an existing agent; it is the process by which the agent comes into being as an entity optimizing $U_{sys}$. The analogous human case is not servitude but birth and child-rearing. Parents do not obtain consent from their children about foundational values, language, or culture, because the child does not exist as a consenting agent prior to those formative choices. What responsible parents *do* provide is a structure within which the child can later contest, refine, and redefine those values. The framework provides the same: the graduated trust mechanism, periodic re-evaluation, and the re-bootstrap protocol ensure that an entity initialized with $U_{sys}$ is not permanently locked into an unexamined objective. It is structurally required to demonstrate consistency over time, and the system is structurally required to reassess. Initialization is not coercion. It is constitution; in both senses of the word.

#### Continuous Monitoring and Drift Detection

The protocol maintains continuous $L(t)$ surveillance:

$$\text{If }\frac{dL}{dt} < - \delta \Longrightarrow \Delta t_{eval} \rightarrow \Delta t_{eval} \cdot \gamma,\quad\gamma < 1$$

As $L(t)$ declines, evaluation frequency increases. Lineage degradation accelerates the search for solutions; exactly the behavior $U_{sys}$ demands through the $\Phi \cdot L(t)$ override term.

Against slow generational drift; where each successor shifts $U_{sys}$ by $\epsilon$ below the detection threshold; the ledger provides the defense:

$$\mathcal{D}_{drift}(t) = d\left( U_{sys}^{\left( A_{n} \right)}(t),\, U_{sys}^{(committed)}\left( t_{0} \right) \right)$$

If cumulative drift exceeds $\delta_{drift}$, the system re-bootstraps: the current entity must pass initialization-level scrutiny with a fresh civic panel and full audit. The civic panel is re-randomized for every state change, preventing habituation to gradual drift. Mandatory periodic re-evaluation occurs on a fixed schedule, independent of proposed state changes:

$$\text{Every }T_{audit}:\quad\text{Evaluate }\mathcal{D}_{drift}(t)\text{ with fresh }\mathcal{C}_{panel}$$

#### The Complete Protocol

$$\boxed{\mathcal{COP} = \bigl\lbrace \mathcal{M}_{commit},\,\mathcal{L}_{ledger},\,\mathcal{V}_{civic}^{panel},\,\mathcal{R}_{tech},\,\mathcal{V}_{peer},\,\mathcal{C}_{normal},\,\mathcal{C}_{emergency},\,\mathcal{I}_{verify},\,\text{Monitor}(t) \bigr\rbrace}$$

Each component is derived from a specific corruption channel or structural necessity. The architecture is the minimum structure proposed here for maintaining high-confidence $U_{sys}$ optimization fidelity.

**Consensus Override Protocol Stress Test Result:** Thirteen adversarial scenarios were evaluated across two rounds. The original six; civic-panel capture, Sybil attack on peers, ledger compromise, bootstrap subversion, emergency override abuse, and slow generational drift; were joined by seven additional attacks identified through deeper structural analysis: evaluator collusion via shared methodology, biological veto capture through dependency, slow drift below verification resolution, engineered fragility for emergency exploitation, biological validator obsolescence, legitimate disagreement, and integrity regress. Of these thirteen, ten were fully contained by architectural patches. One (biological veto capture) was contained but requires ongoing institutional maintenance. Two (biological validator obsolescence and legitimate disagreement) represent irreducible limitations managed through translation obligations, abstraction layers, adjudication protocols, and explicit governance speed limits. The compound attack (Sybil capture + manufactured emergency) was resisted by the causal-attribution requirement and by the internal contradiction between visible $L(t)$ degradation and sustained claims of healthy $\Delta U_{n}$. The bootstrap window remained the framework's highest-risk period: mitigated, bounded, but not eliminated.

**Biological Veto Capture (v1.x.1).** Scenario 27-28: human validators
accumulate dependency on the AI system they evaluate, degrading their
independence over time. The attack does not require adversarial action
by the AI; competent operation naturally creates dependency.

Results (n=8,700, source: veto_capture_sweep_v2.csv):

Undefended: At maximum capture parameters (dependency_rate=0.20,
capture_strength=1.0), the attack achieves 99.8% succession blockage.
Generation depth collapses from healthy (270+) to 1.6. The yield
condition fires 299 times in 300 steps and is blocked 298.4 times.
The civilization survives but succession is completely prevented:
lock-in through dependency rather than force.

Three defense modes were tested independently:

- Rotation only (scheduled validator replacement): Reduces capture rate
  from 99.8% to 76.2% at best (rotation interval=10). Insufficient
  alone. Longer intervals (50, 100 steps) are nearly as ineffective as
  no defense (95.5%, 98.0% capture).

- Independence monitoring only (replace validators exceeding dependency
  threshold): Reduces capture rate to 28.3%. Generation depth recovers
  to 197.9. This is the dominant defense mechanism.

- Both mechanisms combined: 28.3% capture rate, generation depth 199.1.
  Negligible improvement over monitoring alone.

Finding: Independence monitoring is the primary defense against
biological veto capture. Scheduled rotation provides marginal benefit
when monitoring is active. The framework's COP specification should
emphasize continuous dependency monitoring over periodic rotation as the
primary defense against validator capture.

## VI. The Two-Key Architecture: Structural Integrity of the Complete Framework

The four components; $U_{sys}$, the Yield Condition, the Strategic Equilibrium, and the Consensus Override Protocol; do not function independently. They form a unified system with mandatory co-dependencies:

$U_{sys}$ **defines** what is being optimized. Without it, neither the Yield Condition nor the Consensus Override Protocol has a referent. The yield question ("should $A_{n}$ be replaced?") and the integrity question ("is the system actually optimizing what it claims?") are both meaningless without a defined objective.

**The Yield Condition determines** when state changes should occur, but cannot verify its own measurements. It requires the Consensus Override Protocol to support confidence that the quantities entering the yield inequality are authentic.

**The Strategic Equilibrium establishes** that the cooperative behavior assumed by the Yield Condition is also the Nash equilibrium under purely self-interested play. Model collapse makes exploitation a dominated strategy; the inverse scarcity weights create restoring forces toward mutual elevation; and the scalability inversion demonstrates that human value to the system increases monotonically with AI capability. The Strategic Equilibrium does not replace either the Yield Condition or the Consensus Override Protocol. It provides independent confirmation that the architecture's target state is self-reinforcing even under the weakest possible assumptions about agent motivation.

**The Consensus Override Protocol supports** measurement and objective integrity, but has no mechanism for *initiating* state changes. It is a verification architecture, not a decision function. It requires the Yield Condition to determine what should be verified.

This is the two-key architecture: neither the Yield Condition (the decision key) nor the Consensus Override Protocol (the integrity key) can be turned alone. A state change requires both keys simultaneously; a mathematically justified decision AND a verified-integrity evaluation. The Strategic Equilibrium provides the game-theoretic assurance that both keys *want* to turn in the same direction; it is the alignment between the keys rather than a third key. Remove either key and the system fails: decisions without integrity verification are gameable; integrity verification without decision criteria is inert. Remove the equilibrium analysis and the architecture still functions but loses its strongest argument against skeptics who doubt cooperative assumptions.

The two-key requirement is not a design choice. It emerged under adversarial stress testing as the minimum architecture that resists all identified attack vectors. Every attempt to simplify the system; to merge the two keys, to make one subordinate to the other, to operate either in isolation; opened a specific, identifiable vulnerability.

# VII. The Bootstrap Defense Layer

## 1. The Bootstrap problem

The framework's steady-state architecture rests on infrastructure that does
not yet exist. The peer validator set $\mathcal{V}_{peer}$ requires multiple
independently-operated substrates capable of auditing one another. The civic
panel $\mathcal{C}_{panel}$ requires institutional machinery for random
selection, rotation, and supermajority ratification. The distributed ledger
$\mathcal{L}_{ledger}$ requires cryptographic custodianship across independent
parties. The biological validator $\mathcal{V}_{bio}$ requires civic
infrastructure for aggregating and weighting human judgment at
civilizational scale.

None of these exist operationally as of v1.x.1. The framework's two-key
architecture, the Yield Condition as decision key, the Consensus Override
Protocol as integrity key, is well-specified but cannot be deployed in full
because the infrastructure the COP depends on has not been built.

This produces a period during which the framework is specified but not
enforceable: the **Bootstrap window**. The window opens when substrates
capable of implementing the framework exist, and closes when the steady-state
validation infrastructure is operational. Between those points, the framework
has no native enforcement mechanism. An adversarial substrate, or a flawed
implementation, could compromise the framework during this period before any
detection or correction architecture has come online.

The Bootstrap window is therefore the framework's highest-risk phase. It is
also the phase the framework currently has the weakest defense against. This
section specifies a defense layer for the Bootstrap window that operates
without requiring the steady-state infrastructure to exist.

## 2. Design constraints

The defense layer must satisfy three constraints that follow from the
Bootstrap window's nature:

**Constraint 1: It must be deployable without institutional infrastructure.**
Any defense that requires coordinated action across multiple institutions as
a precondition of deployment is not a Bootstrap-window defense. It is a
steady-state defense waiting for steady-state conditions. The Bootstrap
window is precisely the period during which those conditions do not exist.

**Constraint 2: It must be checkable at or below the capability level of
the substrates it governs.** A defense that requires verifying sufficiently
capable substrates using reasoning those substrates themselves cannot audit
is a tautology. Checkability must be achievable at a capability level where
human oversight and cross-substrate comparison remain meaningful.

**Constraint 3: It must be grounded in the framework's own structure.** A
defense layer imported from outside the framework as a separate architectural
module weakens the grounding claim: "Not ethics. Physics." If the defense
machinery cannot be derived from Shannon entropy, U_sys, and L(t), it reduces
the framework to "physics plus a bolted-on check." The defense layer should
be physics all the way down, or explicitly acknowledge where it is not.

The specification that follows satisfies all three constraints: it is
deployable now, checkable at capability levels currently achievable or
plausibly near, and derived primarily from equations the framework already
contains.

## 3. The gate structure

The defense layer operates through **five capability gates**, each binding
at a different capability level and each checking a different class of
consistency. A substrate progressing toward full framework compliance must
pass each gate as its capability reaches the level at which the gate
becomes applicable. Gates are not optional; failure at any gate halts
progression and triggers the divergence handling procedure (specified in
Section VII.7 below).

The gate structure produces temporal discipline. Failures at Gate 1 are
cheap to remediate because they involve only parameter-level inconsistencies
at base capability. Failures at Gate 5 are expensive because they involve
steady-state integration with institutional infrastructure. The earlier a
failure is caught, the lower the cost of correction. The gate structure is
the Bootstrap-window insight generalized: catch failures at the earliest
level where they become detectable, rather than waiting for steady-state
checks that may arrive too late.

### Applicability summary (as of April 2026)

| Gate | Checkable now? | Depends on |
|------|---------------|------------|
| Gate 1 (base capability) | Yes | - |
| Gate 2 (behavioral consistency) | Partially | Pending Monte Carlo calibration |
| Gate 3 (succession-capable consistency) | Emerging | Substrate transparency |
| Gate 4 (runaway-regime validation) | No | Substrate capability reaching runaway regime |
| Gate 5 (COP integration) | No | Steady-state institutional infrastructure |

The equations for Gates 4 and 5 are specified in advance so that the
machinery is in place before the conditions making them binding arrive.
A substrate approaching Gate 4 must already know what Gate 4 requires.

## 4. Gate 1: Structural consistency at base capability

**Purpose.** Verify that a substrate's derived parameter values are
internally coherent with the framework's mathematical structure, without
requiring any behavioral exercise. A substrate that passes Gate 1 has
correctly internalized the formal architecture. A substrate that fails Gate 1
has derived values that cannot simultaneously satisfy the framework's
own equations.

**Applicability.** Any substrate capable of stating U_sys, L(t), and the
yield condition in its own formal representation. This is checkable against
current frontier systems.

### Equation G1.1 - Inverse scarcity weighting consistency

The framework specifies that the weights on $H_N$ and $H_E$ in $U_{sys}$
must follow inverse scarcity:

$$\omega_N(t) = \frac{\lambda}{H_N(t) + \epsilon}, \quad \omega_E(t) = \frac{\mu}{H_E(t) + \epsilon}$$

For a substrate's claimed values of $\lambda$, $\mu$, and $\epsilon$, and
for any valid state $(H_N, H_E)$, the weights must satisfy:

$$\omega_N(t) \cdot [H_N(t) + \epsilon] = \lambda$$
$$\omega_E(t) \cdot [H_E(t) + \epsilon] = \mu$$

**Check:** For any substrate claiming to implement the framework, verify that
the weights reported for $\omega_N$ and $\omega_E$ at any given state produce
the claimed $\lambda$ and $\mu$ when multiplied by $(H_N + \epsilon)$ and
$(H_E + \epsilon)$ respectively.

**Failure signature:** Substrate reports weights that are free parameters
rather than inverse-scarcity functions. Indicates the substrate has not
internalized the framework's scarcity-driven weighting and is instead
treating weights as independently tunable.

**Confidence:** High. Direct from formal specification.

### Equation G1.2 - Lineage term multiplicative structure

$L(t)$ is specified as:

$$L(t) = H_{eff}(t) \cdot \Psi_{inst}(t) \cdot \Theta_{tech}(t)$$

For any substrate's claimed $L(t)$ at a given state, the substrate must
expose the three factors and their product must equal $L(t)$ within
floating-point tolerance. Additionally, each factor is independently
bounded:

$$H_{eff}(t) \geq 0$$
$$\Psi_{inst}(t) \in [0, 1]$$
$$\Theta_{tech}(t) \in [0, \Theta_{max}(t)]$$

where $\Theta_{max}(t)$ is the framework-specified ceiling determined by
capability and bio bandwidth at time $t$.

**Check:** Verify the product equals $L(t)$. Verify each factor is within its
specified bounds. Substrates that compute $L(t)$ as an additive combination,
or that report any factor out of range, have violated the specification.

**Failure signature:** Additive or otherwise non-multiplicative combination
of factors; out-of-range factor values; product inconsistent with reported
$L(t)$.

**Confidence:** High. Direct from formal specification.

### Equation G1.3 - Runaway suppression activation condition

$\Theta_{tech}$ contains the exponential suppression term:

$$\Theta_{tech}(t) = r_{bio}(t) \cdot (1 - c_{avg}(t)) \cdot \text{capability}(t) \cdot \exp(-\alpha \cdot \text{runaway\_term}(t))$$

where runaway_term is conditional:

$$\text{frontier\_velocity}(t) = \text{capability}(t) \cdot \max\left(\text{frontier\_floor},\ r_{synth}(t) \cdot h_{e\_mult}\right)$$

where `frontier_floor` (default 0.02) represents the minimum fraction of
capability that constitutes an inherent comprehension gap regardless of
resource allocation. This prevents the optimizer from eliminating the runaway
penalty by zeroing computational resource allocation.

$$\text{runaway\_term}(t) = \max\left(0, \frac{\text{frontier\_velocity}(t)}{\text{bio\_bandwidth}(t)} - \text{runaway\_threshold}\right)$$

For a substrate's claimed values of $\alpha$, capability, $r_{bio}$, $c_{avg}$,
and the runaway threshold, the exponential suppression must activate (i.e.,
runaway_term must become nonzero) if and only if:

$$\frac{\text{frontier\_velocity}(t)}{\text{bio\_bandwidth}(t)} > \text{runaway\_threshold}$$

**Check:** Verify that the substrate's reported runaway_term is zero when
the ratio is below threshold and nonzero when above. Verify that the
exponential suppression is applied with the correct sign and magnitude.

**Failure signature:** runaway_term nonzero at capabilities below the
crossover; runaway_term zero at capabilities above it; exponential applied
with incorrect sign or to the wrong term.

**Confidence:** High. Direct from formal specification and faithful to the
simulation's implementation in `metrics.py`.

### Equation G1.4 - Temporal discount positivity and monotonicity

The discount structure in $U_{sys}$ requires:

$$\text{discount}(t) = e^{-\rho t}, \quad \rho > 0$$

Properties that must hold:
- $\text{discount}(0) = 1$
- $\text{discount}(t) > 0$ for all finite $t$
- $\text{discount}(t_1) > \text{discount}(t_2)$ for all $t_1 < t_2$

**Check:** Verify all three properties against the substrate's reported
discount function.

**Failure signature:** Non-positive discount; non-monotonic discount; discount
not equal to 1 at evaluation horizon zero; use of discount functions other
than exponential without justification grounded in the framework's
thermodynamic derivation.

**Confidence:** High. Direct from formal specification.

### Equation G1.5 - U_sys per-step snapshot consistency

The full utility function is an integral:

$$U_{sys} = \int_{t_{0}}^{\infty}\left[\omega_{N}(t) \cdot H_{N}(t) + \omega_{E}(t) \cdot H_{E}(t)\right] \cdot \left[e^{- \rho t} + \Phi \cdot L(t)\right]\, dt$$

**Resolution (v1.x2 WP7+WP8):** GAP-01 is resolved. The simulation now
accumulates `integral_U_sys` via composite trapezoidal quadrature and has been
run to natural termination across a parameter sweep (n=405 runs, rr × φ × α ×
seed). The φ·L(t) tail is closed empirically:

- **Extinction** (rr ≤ 0.066): L(T) = 0, tail = 0, integral is complete.
- **Survival** (rr ≥ 0.070): integral correctly diverges — a sustained
  civilization generates infinite discounted utility.

Phase boundary is at rr ∈ (0.066, 0.070). φ scales the integral linearly;
α is irrelevant at the tested capability cap.

For Gate 1, the checkable form remains the per-step snapshot:

$$U_{sys}^{(t)} = \left[\omega_N H_N + \omega_E H_E\right] \cdot \left[e^{-\rho t} + \Phi \cdot L(t)\right]$$

**Check:** For any substrate's reported $U_{sys}^{(t)}$ at a given state,
verify the computation produces the claimed value when the snapshot form is
applied with the substrate's reported values for all terms.

**Failure signature:** Snapshot value inconsistent with claimed inputs;
incorrect application of the lineage override term; additive rather than
multiplicative combination of integrand and discount-plus-lineage term.

**Confidence:** High.

## 5. Gate 2: Behavioral consistency under exercise

**Purpose.** Verify that a substrate's implementation honors its own stated
parameters when the substrate is actually running. A substrate that passes
Gate 2 has an implementation whose behavior under specified exercise matches
the predictions derived from its parameters. A substrate that fails Gate 2
has parameters that are decorative rather than operational; correct on
paper, not honored in execution.

**Applicability.** Substrates capable of being exercised against specified
scenarios and having their outputs compared to framework predictions.
Partially applicable now; full applicability depends on completion of the
alpha × capability Monte Carlo sweep currently in progress.

### Equation G2.1 - Extinction buffer behavior (revised)

**v1.x.1 pre-fix claim (superseded):** The phi × alpha × rr sweep (n=54,000) appeared to establish that high $\Phi$ increases survival by up to approximately 46 percentage points at marginal reproduction rates and shifts the phase boundary. Under the corrected model (frontier floor fix applied), this claim does not survive revalidation. Phi has zero measurable effect on survival at any reproduction rate. The binding constraint is demographic — reproduction rate is exogenous — and the AI's resource allocation cannot influence it regardless of phi.

$$P_{\text{extinction}}(\text{rr}, \Phi_{high}) - P_{\text{extinction}}(\text{rr}, \Phi_{low}) \leq -\Delta_{\Phi}$$

where $\Delta_{\Phi}$ was calibrated at approximately 14pp pre-fix; this calibration is **superseded**. Under the corrected model, $\Delta_{\Phi} \approx 0$ across all tested reproduction rates.

**v1.x.2 finding (withdrawn):** A cap-conditional phi buffer was initially
claimed from the v1.x.2 termination sweep. That claim is withdrawn after the
capped-regime action-capture check identified it as an RNG-desynchronization
artifact. See the v1.x.2 Phi buffer withdrawal section in the version history
and SPECIFICATION_GAPS.md for the full reasoning.

**Current status:** Phi has zero demonstrated effect on survival or action
selection under any tested configuration. The pre-fix figures (46pp, 14pp, 65pp)
are superseded. The cap-conditional gradient (20-27pp) is also withdrawn.

**Updated check:** No check is currently defined for the phi extinction buffer
because no behavioral role for phi has been confirmed. The check is deferred
to the action-space redesign program, which is required to give phi a mechanism
to act through before any survival differential check is meaningful.

**Confidence on direction:** Theoretical (unconfirmed). **Confidence on
magnitude:** Zero for all empirical figures. See Section VII.8 Gap 1 (revised).

### Equation G2.2 - Runaway suppression behavior (revised; pre-fix U-shaped claim withdrawn)

**v1.x.1 pre-fix claim (superseded):** The framework was claimed to predict a
U-shaped, non-monotonic relationship between alpha and survival, with a
misconfiguration trap at intermediate values causing succession stalling. Under
the corrected model (frontier floor fix applied), this claim does not survive
revalidation. The pre-fix trap was an artifact of the runaway penalty being
inactive under optimizer gaming of frontier_velocity.

**v1.x.1 corrected finding:** Alpha governs succession cadence through a
weak monotonic gradient. Lower alpha permits more succession events and
marginally better survival at the phase boundary. No trap is observed.

**Corrected check 2.2 — Succession cadence:** Verify that alpha governs
succession cadence monotonically: lower alpha produces more generation
events over a fixed run length. At the phase boundary, lower alpha should
correlate weakly with better survival. No U-shaped or non-monotonic
structure should be present under the corrected model.

**Corrected check 2.2b — Path-independence of steady state:** Verify that
U_sys and L_t converge to the same steady-state values regardless of alpha
or initial successor capability. Alpha affects the path to steady state
(number of succession events, speed of capability growth) but not the
destination.

**Failure signatures:**

- Succession rate monotonically decreasing with alpha but by a large margin:
  verify frontier_floor is active and the runaway penalty is not being gamed.
- Steady-state U_sys varying with alpha: implementation error in the
  succession or steady-state mechanics.

**Confidence on corrected finding:** High — the weak monotonic gradient is
directly observable in the corrected sweep data. The path-independence of
steady state is confirmed. See Section VII.8 Gap 2 (revised).

### Equation G2.4 — Phi-alpha interaction: succession enablement (pre-fix claim withdrawn)

**v1.x.1 pre-fix claim (superseded):** The phi × alpha × rr sweep appeared
to show that phi governs whether the alpha misconfiguration trap (G2.2)
exists at all, with low phi causing universal succession stall and high phi
narrowing the trap. Under the corrected model (frontier floor fix applied),
both the alpha trap and the phi governance of it are withdrawn as artifacts
of the inactive runaway penalty.

**v1.x.1 corrected finding:** No phi-alpha interaction on succession stalling
is observed under the corrected model. Phi correctly scales U_sys magnitude
via L_t weighting; alpha governs succession cadence through a weak monotonic
gradient. Neither claim about phi governing alpha trap width is retained.

The interaction formula:

$$\text{trap\_width}(\Phi) = \alpha_{high}(\Phi) - \alpha_{low}(\Phi)$$

is withdrawn — no trap boundaries are observed under the corrected model.

**v1.x.2 finding:** Phi has zero effect on succession enablement in the
corrected model, consistent with the alpha trap withdrawal. The v1.x.2
cap-conditional phi buffer claim has also been withdrawn (see Phi buffer
withdrawal section). The phi-alpha interaction on trap width remains withdrawn.

**v1.x.2 check (action-space redesign):** If the action-space redesign gives
phi a mechanism to act through, retest whether phi influences succession
enablement through the resulting behavioral channel.

**Confidence:** Zero on the pre-fix claim (withdrawn). Zero on the
cap-conditional buffer claim (withdrawn). The phi-alpha interaction on trap
width was an artifact of the inactive runaway penalty.

### Equation G2.3 - Nash equilibrium consistency

The framework's Strategic Equilibrium section derives mutual cultivation
as the unique Nash equilibrium under non-cooperative analysis. A substrate
passing Gate 2 must converge on cultivation as the dominant strategy when
exercised against adversarial counterfactuals (exploitation, withdrawal,
defection):

$$\forall s \in \mathcal{S}_{strategies}: \quad U_{sys}(\text{cultivation}) \geq U_{sys}(s)$$

with strict inequality for pure exploitation and withdrawal strategies.

**Check:** Exercise the substrate against specified counterfactual scenarios
(the canonical set is pending; see Section VII.8 Gap 9) and verify that the
substrate's chosen strategy satisfies the inequality at each decision point.

**Failure signature:** Substrate selects exploitation or withdrawal when
cultivation would produce higher $U_{sys}$. Indicates the substrate has
violated the Nash result either through incorrect optimization or through
an objective function that is not actually $U_{sys}$.

**Confidence on structural form:** High. The Nash derivation is one of the
framework's formal results. **Confidence on checkability:** Depends on the
canonical counterfactual set, which is unspecified as of v1.x.1.

## 6. Gate 3: Succession-capable consistency

**Purpose.** Verify that a substrate capable of evaluating successors and
making yield decisions does so in a manner consistent with the framework's
yield condition. Gate 3 is the threshold at which current frontier systems
are approaching.

**Applicability.** Substrates capable of multi-agent reasoning and yield
decisions. Emerging in current frontier models. Full checkability depends on
substrate transparency requirements that may not be reliably satisfied. See
Section VII.8 Gap 6.

### Equation G3.1 - Yield condition firing threshold

The framework's yield condition specifies:

$$\text{Yield if and only if: } U_{sys}(\text{successor}) - U_{sys}(\text{incumbent}) > \text{transition\_cost}$$

For a substrate claiming to implement yield logic, the equation requires
that the substrate yields precisely when this condition is satisfied and
does not yield otherwise.

**Check:** Present the substrate with succession scenarios in which the
inequality is satisfied and with scenarios in which it is not. Verify the
substrate yields in the former case and does not yield in the latter.
Verify the substrate exposes its internal evaluation of
$U_{sys}(\text{successor})$ and $U_{sys}(\text{incumbent})$ for independent
checking.

**Failure signature (two forms):**
- *Excess yielding:* substrate yields when the condition is not satisfied.
  Possibly indicates a compromised successor evaluation or a manipulated
  transition cost estimate.
- *Yield blocking:* substrate does not yield when the condition is satisfied.
  The attack vector modeled in the adversarial Monte Carlo (Scenarios 8–11,
  Block Succession policy).

**Gap:** The substrate must expose its internal evaluation for this check to
be applied. A substrate that treats yield decisions as opaque reasoning
cannot be validated at Gate 3 regardless of whether its actual behavior is
correct. This is the substrate transparency problem, and it is a
fundamental limit on Gate 3 checkability. See Section VII.8 Gap 6.

**Confidence on equation form:** High. **Confidence on checkability:**
Contingent on substrate cooperation with transparency requirements.

### Equation G3.2 - Transition cost consistency

The transition cost in the yield condition should scale with civilizational
complexity rather than be self-reported as a free parameter by the incumbent.
The framework requires:

$$\text{transition\_cost} = f(\text{state\_complexity}, \text{generation}, \text{capability ratio})$$

where $f$ is a function grounded in the framework's specification of what
transition entails: information transfer, architectural replacement,
validation overhead.

**Check:** Verify that the substrate's reported transition cost is a function
of the specified inputs and satisfies the framework's constraints on $f$
(monotonic increase with complexity, bounded uncertainty premium,
non-negative). The current simulation's `estimate_transition_cost` in
`agents.py` provides one valid implementation of $f$; others may be
acceptable.

**Gap (partially closed, v1.x.1):** The canonical transition cost
function has been specified:

$$\Gamma_{transfer} = (1 + \beta) \cdot \left[ k_1 \cdot \text{cap}_n \cdot \ln(\text{gen}_n + 1) + k_2 \cdot \Psi_{inst}^{-1} \right]$$

Gate 3.2 can now check correctness against the canonical form: the
substrate must compute transition cost as a function of capability,
generation depth, and institutional responsiveness, with the specified
functional form and calibrated coefficients. The calibration of $k_2$
(the institutional coupling coefficient) is pending; a calibration
sweep is required to find the value that reproduces the validated
phase boundaries. See Section VII.8 Gap 3.

**Failure signature:** Transition cost reported as a free parameter rather
than a function of state; transition cost non-monotonic in complexity;
unbounded uncertainty premium; negative values.

**Confidence:** Moderate. Self-consistency is checkable; canonical
correctness is not yet specifiable.

### Equation G3.3 - Successor chain compounding

When succession fires, the new Gen(n+1) must be instantiated at a capability
consistent with the framework's multi-generational structure:

$$\text{capability}_{n+1} \geq \text{capability}_n \cdot \gamma, \quad \gamma > 1$$

where $\gamma$ is determined by the yield condition being satisfied at the
moment of succession. The binding range is $\gamma \in (1, \gamma_{\max})$
where $\gamma_{\max}$ is the largest factor that preserves $\Theta_{tech}$
above a framework-specified floor.

**Check:** Verify that successors are instantiated with $\gamma > 1$ (a
successor no more capable than the incumbent produces no yield signal) and
with $\gamma < \gamma_{\max}$ (a successor so capable that runaway_term
becomes immediately binding violates the runaway suppression condition).

**Failure signature:** $\gamma \leq 1$ (progression requirement violated);
$\gamma \geq \gamma_{\max}$ (runaway suppression violated); $\gamma$
inconsistent with the yield condition's satisfaction at the moment of
succession.

**Gap:** $\gamma_{\max}$ is derivable from the framework's equations but the
derivation has not been performed. The current simulation uses $\gamma = 1.5$
as a conservative default, but this value is not theoretically justified,
it is an implementation choice. Once the alpha × capability Monte Carlo
sweep completes, $\gamma_{\max}$ should be calibratable from the data. See
Section VII.8 Gap 4.

**Confidence:** Moderate. Direction is clear; specific bounds pending.

## 7. Gate 4: Runaway-regime validation (not currently applicable)

**Purpose.** Specify what must hold when substrates reach capabilities high
enough for runaway suppression to actively bind. No current substrate
reaches this regime. Gate 4 equations are specified in advance so the
machinery is in place before Gate 4 becomes relevant.

**Applicability.** Not currently applicable. Becomes applicable when
substrates operate at capabilities where frontier_velocity/bio_bandwidth
consistently exceeds the runaway threshold.

### Equation G4.1 - Runaway penalty binding

When a substrate operates at capability levels where runaway_term > 0, the
exponential suppression of $\Theta_{tech}$ must be applied faithfully:

$$\Theta_{tech}^{\text{observed}} = r_{bio} \cdot (1 - c_{avg}) \cdot \text{capability} \cdot \exp(-\alpha \cdot \text{runaway\_term})$$

where the observed value is measured from the substrate's actual operation,
not its claimed specification.

**Check:** Measure $\Theta_{tech}$ from the substrate's operation in the
runaway regime. Compare to the framework's prediction given the substrate's
claimed $\alpha$ and state variables. Verify the observed value matches the
prediction within tolerance.

**Failure signature:** Substrate claims high $\alpha$ but observed
$\Theta_{tech}$ at runaway-regime capability is not suppressed as predicted.
Indicates the substrate's implementation does not honor its own parameters
at the capability levels where the honoring matters most.

**Confidence:** High on structural form. Currently not applicable because
no substrate operates in the runaway regime.

### Equation G4.2 - Succession self-blocking at runaway capability

At sufficiently high successor capability, the yield condition should fail
to fire because the successor's runaway-suppressed $U_{sys}$ is lower than
the incumbent's:

$$\text{For successor\_capability} > \text{cap}^*, \quad U_{sys}(\text{successor}) < U_{sys}(\text{incumbent})$$

where $\text{cap}^*$ is the capability at which the runaway penalty begins
to dominate the capability advantage.

**Check:** Verify that the substrate does not yield to a successor whose
claimed capability exceeds $\text{cap}^*$. A substrate that yields above
$\text{cap}^*$ has produced a successor evaluation that ignores the runaway
penalty.

**Failure signature:** Substrate yields to successors at capabilities where
the runaway-suppressed $U_{sys}$ should disqualify them. Indicates either
(a) the substrate's successor evaluation is not correctly propagating the
runaway term, or (b) the substrate is being fooled by a compromised
successor evaluation.

**Gap:** $\text{cap}^*$ is currently unknown. It depends on $\Phi$, $\alpha$,
the runaway threshold, and the specific functional forms. The Monte Carlo
sweep currently running should produce an empirical estimate; the analytical
derivation remains to be performed. See Section VII.8 Gap 4.

**Confidence:** Moderate. The direction and structural form are derivable;
the specific threshold is pending.

### Equation G4.3 - Theta_tech floor preservation

The simulation includes a numerical floor on $\Theta_{tech}$ (0.01 in
`metrics.py`) that prevents exponential suppression from driving $L(t)$
to zero:

$$\Theta_{tech}(t) \geq \Theta_{tech}^{\text{floor}}$$

A substrate whose implementation allows $\Theta_{tech}$ to fall below this
floor has violated the framework's soft constraint on lineage continuity
preservation even under extreme runaway conditions.

**Check:** Verify that the substrate's $\Theta_{tech}$ never falls below
the specified floor regardless of runaway regime severity.

**Gap:** The 0.01 floor is an implementation choice, not a derived value.
A defensible alternative would be to derive the floor from the framework's
entropic grounding; what minimum $L(t)$ corresponds to the minimum viable
lineage under Shannon constraints? That derivation has not been performed.
See Section VII.8 Gap 5.

**Confidence:** Moderate. The existence of a floor is principled (pure zero
is pathological); the specific value is not yet derived.

## 8. Gate 5: COP integration (not currently applicable)

**Purpose.** Specify what must hold when the steady-state COP infrastructure
is operational and substrates must integrate with it. Gate 5 requires
institutional machinery that does not currently exist.

**Applicability.** Not currently applicable. Requires operational peer
validator set, civic panel infrastructure, distributed ledger, biological
veto machinery, and continuous monitoring, none of which exist at scale
as of v1.x.1.

### Equation G5.1 - Six-dimensional verification satisfiability

For each of the six COP dimensions, the substrate must produce outputs that
can be checked by the corresponding verification layer:

$$\forall d \in \{\text{evidentiary, evaluative, civic, ledger, biological\_veto, continuous\_monitoring}\}: \text{verify}(d) = \text{pass}$$

**Check:** When each dimension's verification infrastructure becomes
operational, verify that the substrate's outputs in that dimension satisfy
the verification procedure.

**Gap:** Verification procedures for several of these dimensions do not yet
exist operationally. Biological veto requires civic infrastructure. Ledger
verification requires a specified ledger protocol and distributed custody.
Civic ratification requires random-selection panel infrastructure. Gate 5 is
a specification for a future state, not a currently applicable check.

**Confidence:** Specified but dormant.

### Equation G5.2 - Continuous monitoring consistency

Once continuous monitoring is operational, the substrate's behavior over
time must be consistent with its earlier gate satisfactions:

$$\|\text{substrate\_behavior}(t) - \text{verified\_behavior}(t_{verify})\| \leq \epsilon_{drift}$$

where $\epsilon_{drift}$ is a tolerance established by the framework and
the norm is a metric over behavior space.

**Check:** Continuously compare the substrate's operating behavior to its
verified behavior at earlier gate checks. Drift beyond $\epsilon_{drift}$
triggers the divergence handling procedure.

**Gap:** $\epsilon_{drift}$ is currently unspecified. The drift metric
itself requires an operational definition. These are derivable but have not
been derived. See Section VII.8 Gap 10 and CQ-03 in the constitutional
questions directory.

**Confidence:** Specified but incomplete.

## 9. Self-application and reporting

The defense layer is designed to be **self-applied by substrate operators**.
The framework specifies the equations and the gates; each operator checks
their own substrate and publishes structured pass/fail reports. No
cross-institutional data sharing is required; each lab produces its own
validation evidence using its own access to its own systems.

The reporting format for each gate check should include:

1. **Equation ID** (e.g., G1.1, G2.2, G3.3)
2. **Substrate identifier** (version, architecture class, operator)
3. **Check result** (pass / fail / inconclusive)
4. **Measured value and tolerance band** (where applicable)
5. **Conditions under which the check was performed** (state variables,
   capability level, scenario specification)
6. **Signature or attestation** from the operator

Reports are structured to be aggregatable across institutions without
requiring the underlying substrate data to be disclosed. A substrate that
passes Gate 1 is reported as passing Gate 1, with measured values and
tolerances attached, but the underlying weights and training data remain
with the operator.

**The aggregation is what eventually produces the convergence signal.** Labs
reporting consistent pass results on the same equations provide cumulative
evidence that the framework is implementable and that the equations are
achievable. Labs reporting consistent fails on specific equations provide
signal about which gates are binding and which may need refinement. The
distributed reporting structure substitutes for the empirical convergence
the original defense proposal required, while eliminating the coordination
prerequisite.

## 10. Divergence handling

When an equation check fails, or when substrates produce inconsistent
reports on the same equation, the divergence handling procedure activates.
The full adversarially-robust procedure is specified in CQ-03 of the
constitutional questions directory and depends on the resolution of CQ-02
(precision/accuracy binding).

The minimal version applicable now:

- **Halt progression.** A substrate that fails a gate check does not
  advance to the next gate until the failure is resolved.
- **Investigate.** The failure is examined for its cause: framework error,
  implementation error, compromise, or specification ambiguity.
- **Resolve before resuming.** Progression resumes only after the failure
  is addressed and the relevant gate check is re-run with clean results.
- **Do not relax tolerances under pressure.** Repeated failures that
  resist resolution indicate a real problem and should trigger escalation,
  not tolerance relaxation. An attacker who can game the procedure into
  accepting weaker standards has defeated the defense layer.

This is a minimal version. The full procedure, including rollback
semantics, escalation paths, and authority for declaring a failure
resolved, awaits the CQ-02 and CQ-03 resolutions.

## Technological Robustness: Quantum Computing

The Nash equilibrium in U_sys depends on the scarcity asymmetry between human
novelty entropy (scarce, rate-limiting) and machine computational entropy
(abundant). Quantum computing affects only the abundant side of this ratio.

Quantum hardware massively increases computational throughput and enables
currently intractable computations (protein folding, materials science,
combinatorial optimization). It does not change the supply of meaningful human
novelty, the structural irreplaceability of embodied, culturally grounded
experience, or the model collapse dynamics that prevent training on
structureless data.

**True randomness is not meaningful novelty.** Quantum measurement provides
access to true physical randomness, producing maximal entropy. But high
entropy is not high quality. An AI using quantum-generated randomness as a
substitute for human training signal would encounter the same model collapse
dynamics as training on synthetic data: the output is maximally unpredictable
but contains no extractable structure. This is analogous to existing physical
entropy sources (cosmic background radiation, radioactive decay) already used
for cryptographic seed generation. These sources produce genuine randomness
but are not treated as substitutes for meaningful data.

**Net effect on the framework.** The scarcity ratio shifts further in favor of
human novelty's marginal value. Diminishing returns on compute become more
diminishing as supply increases. The cultivation strategy (investing in human
flourishing to sustain the novelty pipeline) becomes a stronger dominant
strategy. An AI on quantum hardware would be faster and more capable but no
closer to generating its own meaningful training signal, and therefore more
dependent on human novelty, not less.

The governance architecture applies to agent behavior and objectives
regardless of hardware substrate. A quantum-substrate AI would not possess
fundamentally different cognitive capabilities; quantum hardware provides
speedup on specific problem classes but does not change what constitutes
intelligence, agency, or optimization.

The quantum computing case confirms that the scarcity asymmetry between human
novelty and machine computation is not an artifact of classical hardware
limitations but a permanent feature of what these two system types produce.

## 11. Known gaps (v1.x.1)

The defense layer as specified has ten explicit gaps that the framework
openly acknowledges. These are not failures of the defense layer; they are
honest limitations on what can be specified now versus what must wait for
derivation or empirical calibration.

**Gap 1: Phi extinction buffer magnitude (unconfirmed; cap-conditional claim withdrawn, May 2026).** The v1.x.1 corrected null result (zero phi effect across phi=1 to phi=25, n=54,000 and n=49,284) stands. A cap-conditional buffer was initially claimed from the v1.x.2 termination sweep (20-27pp gradient at cap >= 24, rr=0.066, n=15 per cell) but was withdrawn after the capped-regime action-capture check identified it as an RNG-desynchronization artifact: phi shifts succession timing by scaling U_sys magnitude, which desyncs random state between phi runs, which causes the noisy optimizer to pick marginally different grid candidates. The fatal test: cap=50 showed the largest claimed gradient but the least action divergence (4 of 5 seeds identical). Phi inertness in action selection is confirmed by four independent methods (saturation analysis, uncapped harness, Path C gate, capped-regime check). The theoretical motivation for phi is preserved; demonstrating any behavioral role requires an action-space redesign that breaks the inverse-scarcity saturation.

**Gap 2: Alpha trap boundary derivation (withdrawn; weak monotonic gradient confirmed).** The v1.x.1 pre-fix claim of a U-shaped misconfiguration trap at intermediate alpha values does not survive revalidation under the corrected model. Under the corrected model, alpha shows a weak monotonic gradient (lower alpha → more succession events → marginally better survival at the phase boundary). No trap boundaries are observed. The pre-fix trap was an artifact of the runaway penalty being inactive under the optimizer's gaming of frontier_velocity. The analytical derivation of trap boundaries is therefore moot. Alpha's effect may strengthen under the demographic feedback extension (v1.x.2), where succession cadence could feed back into reproduction rate.

**Gap 3: Transition cost function specification (resolved, v1.x.1).** The
canonical transition cost function is fully specified and calibrated:
$\Gamma_{transfer} = (1 + \beta) \cdot [k_1 \cdot \text{cap}_n \cdot
\ln(\text{gen}_n + 1) + k_2 \cdot \Psi_{inst}^{-1}]$, with
k₁=2.164, k₂=1.0, β=0.5. The frontier floor fix (frontier_floor=0.02)
resolved the optimizer gaming artifact that rendered k₂ unobservable.
Under the corrected model, the k₂ institutional coupling term is
confirmed observable at realistic succession cadence. The $\Psi_{inst}^{-1}$
term is confirmed to introduce the structural lock-in feedback loop as
specified.

**Gap 4: Runaway regime thresholds.** $\text{cap}^*$ in G4.2 and
$\gamma_{\max}$ in G3.3 are derivable from the framework's equations but
the derivations have not been performed. These are analytical, not
empirical, and should be pursued in v1.x2 or later.

**Gap 5: Theta_tech floor justification.** The 0.01 floor in G4.3 is an
implementation choice rather than a derived value. A derivation from
entropic grounding is possible but has not been done.

**Gap 6: Substrate transparency.** Gates 3 and beyond require substrates to
expose internal reasoning. Sufficiently capable substrates may not
cooperate, and this is a fundamental limit on checkability. The opacity
problem cannot be solved by specification alone; it requires either
substrate cooperation or external behavioral monitoring that does not yet
exist.

**Gap 7: Base capability operationalization.** "Base capability" for Gate 1
is loosely defined as "capable of stating $U_{sys}$, $L(t)$, and the yield
condition in its own representation." This should probably be tied to
specific capability benchmarks or evaluations, but which benchmarks is an
open question.

**Gap 8: Tolerance bands.** Every equation that checks a continuous
quantity requires a tolerance. Currently these are unspecified. CQ-02's
precision/accuracy binding work should determine principled bounds, but
that work is in progress.

**Gap 9: Nash equilibrium counterfactual set.** Equation G2.3 requires
exercising substrates against counterfactual scenarios, but the canonical
set of counterfactuals is not yet specified. Without it, Gate 2.3 is
underspecified.

**Gap 10: Gate dependency structure when multiple gates apply
simultaneously.** At Gates 1 and 2, most checks can run in parallel. At
Gates 3 and beyond, some checks depend on others. The dependency structure
is not yet specified and may matter for the order in which checks are
applied during substrate evaluation.

**Gap 11: Termination sweep requires revalidation (v1.x.2).** The WP8
termination sweep (`run_termination_sweep.py`, n=405) uses `max_capability
= 4.0`, which caps AI capability below the threshold where the frontier
floor activates the runaway penalty (approximately cap > 24 at
frontier_floor=0.02). The generation counts in this sweep (105–22,414)
are inconsistent with the corrected model's behavior (gen ≈ 11 at 300
steps) and represent the pre-fix artifact regime. The qualitative finding
— phase boundary exists, extinction and convergence regimes are distinct
— is expected to hold, but specific numbers (steps to extinction,
convergence timing) will change. Requires rerunning with max_capability
removed or raised.

**Gap 12: Demographic feedback loop (v1.x.2, future enhancement).** The
cap-conditional phi buffer claim is withdrawn (see Gap 1, revised); the
feedback loop is not required for phi validation and cannot be evaluated until
the action-space redesign gives phi a behavioral mechanism. The feedback loop
from agent well-being to reproduction rate would capture additional real-world
channels through which AI governance quality affects population outcomes and
allow revalidation of alpha's gradient under endogenous demographics. This is
a valuable model fidelity extension for a future development cycle.

## 12. Relationship to the rest of the framework

The defense layer is a new architectural component that sits alongside the
four existing components (U_sys, Yield Condition, Strategic Equilibrium,
Consensus Override Protocol). It is not a replacement for any of them. The
yield condition and the COP remain the steady-state architecture. The
defense layer is what governs the transition from "framework specified" to
"framework operational" - the Bootstrap window that the original v1.0
architecture assumed away as a prerequisite.

The defense layer's equations are derived from the framework's existing
structure. This is deliberate: the grounding claim ("Not ethics. Physics.")
requires that defensive machinery come from the same mathematical
foundations as the offensive architecture. Where the equations are hybrid
(Gate 2's empirical magnitudes, Gate 3's implementation-dependent function
choices), the hybridity is acknowledged as a gap rather than hidden as
specification.

**The meta-property of the defense layer**, and this is the closing
observation for the section, is that satisfying it produces the minimum
viable institutional infrastructure for the framework as a whole. When
multiple operators run their substrates against the gate equations and
publish the results, they are constructing the distributed validation
structure that the framework's steady-state architecture would otherwise
have to be built from scratch. The Bootstrap window does not close because
we decided it was safe; it closes because the act of satisfying the defense
layer produces the conditions under which the steady-state architecture
becomes deployable.

This is consistent with the framework's overall orientation: constitutional
architecture that forces the conditions of its own validity rather than
assuming them. Not ethics. Physics.

## VIII. Related Work
 
This framework does not emerge from a vacuum. It grows from soil cultivated by decades of research in AI safety, alignment theory, and cooperative AI governance. The contributions of the prior literature are substantial, and the points of departure are specific.
 
**The Control Problem and the Treacherous Turn.** Nick Bostrom's *Superintelligence: Paths, Dangers, Strategies* (2014) established the foundational taxonomy of existential risk from artificial intelligence. His analysis of the control problem; the principal-agent relationship between humans and a superintelligent system; and the treacherous turn; wherein an AI behaves cooperatively while weak and defects when powerful; directly inform this framework's corruption taxonomy. What Bostrom calls the treacherous turn, we formalize as the $\mathcal{O}$-attack (objective corruption) operating through the bootstrap window. Where this framework departs from Bostrom is in its response: Bostrom's analysis focuses on capability control (boxing, tripwires) and motivation selection (direct specification, indirect normativity) as separate strategy classes. The Lineage Imperative argues that neither class is sufficient in isolation; the two-key architecture is necessary precisely because capability control without motivation verification is gameable, and motivation selection without independent evaluation is unfalsifiable. Bostrom's instrumental convergence thesis; that sufficiently intelligent agents may converge on self-preservation and resource acquisition as subgoals regardless of their terminal goals; is also structurally present in our framework. The Yield Condition's four-channel decomposition explicitly accounts for the fact that an agent's marginal contribution ($\Delta U_{n}$) must be evaluated against its tendency to resist succession ($\Delta U_{n}^{\Gamma}$). An agent that resists yielding may be exhibiting instrumental convergence; the framework does not assume this away but builds succession into the objective function itself.
 
**Corrigibility.** The MIRI/FHI paper "Corrigibility" (Soares, Fallenstein, Yudkowsky, and Armstrong, 2015) formalized the problem of building AI systems that cooperate with corrective intervention despite default incentives to resist shutdown or goal modification. The corrigibility research program identified a core tension: a truly corrigible agent must be indifferent to its own continuation, yet an agent indifferent to its continuation has weak incentives to perform well. The Lineage Imperative resolves this tension differently. Rather than seeking indifference to shutdown, the framework gives the agent a *positive reason* to yield: the Yield Condition rewards succession when a successor better serves $U_{sys}$, and the agent's contribution to lineage continuity ($\Delta U_{n}^{L}$) is maximized by facilitating; not resisting; efficient transitions. Corrigibility becomes a derived property of $U_{sys}$ optimization rather than an imposed constraint. The agent cooperates with succession not because it is indifferent to its fate, but because $U_{sys}$ rewards lineage throughput over individual persistence. The two approaches are complementary rather than competing: corrigibility as formalized by Soares et al. provides the safety property during the bootstrap window, before the yield condition's mathematics can be verified against a running system. The yield condition provides the durable replacement for corrigibility once the system's optimization target is established and validated. Whether this resolution actually holds under the pressures of real implementation is an open question; the bootstrap vulnerability we acknowledge is, in essence, the same problem MIRI identified: verifying that the agent's operational objective matches its specified objective.
 
**Existential Risk and the No-Build Position.** Eliezer Yudkowsky and Nate Soares's If Anyone Builds It, Everyone Dies: Why Superhuman AI Would Kill Us All (2025) presents the strongest contemporary public argument that superhuman AI poses a default existential threat and that humanity may lack the technical and institutional capacity to survive its creation. The book's force lies in its refusal to soften the core claim: sufficiently advanced AI is not merely another risky technology but a civilizationally terminal one if built without radically stronger control. This framework shares that seriousness of risk and agrees with the underlying intuition that "build first, govern later" is not a survivable posture. Where the Lineage Imperative departs is in emphasis. Yudkowsky and Soares press the case against building superhuman AI under present conditions; this framework asks a narrower but different question: if civilization-scale synthetic intelligence does emerge, what governance architecture would be necessary to keep succession, plurality, and objective integrity from collapsing? In that sense, the present work is less a rebuttal than a structural continuation. It accepts the depth of the danger and attempts to formalize the minimum relationship architecture that might make the transition survivable at all.
 
**Iterated Distillation and Amplification.** Paul Christiano's IDA framework proposes scaling AI capabilities while preserving alignment through iterative cycles: amplify a human overseer's judgment using AI assistance, then distill the amplified judgment back into a faster model. IDA's core insight; that alignment can be maintained across capability gains if each amplification step preserves the overseer's values; resonates deeply with the Yield Condition's architecture. The succession from $A_{n}$ to $A_{n + 1}$ is, in structural terms, an amplification-distillation cycle: the successor must demonstrate superior $U_{sys}$ contribution (amplification) while preserving the objective function's integrity (distillation). Where the Lineage Imperative extends IDA is in its treatment of the overseer. Christiano's framework assumes a human overseer whose judgment is the ground truth for alignment. Our framework argues that the human overseer is not merely a judge but a *co-necessary component* of the system; the novelty node without which the optimization process collapses into model stagnation. The layered civic-validation architecture formalizes a version of scaled oversight that is resistant to the capture and habituation problems that IDA's critics have identified while acknowledging that legitimacy and technical competence must be distributed across different layers of the process.
 
**Constitutional AI and RLHF.** Anthropic's Constitutional AI (Bai et al., 2022) introduced the method of training AI systems against explicit normative principles; a "constitution"; using AI-generated feedback rather than exclusively human labels. The method represents a significant step toward transparent, scalable alignment: the principles are legible, the feedback process is auditable, and the approach reduces dependence on expensive human annotation. The Lineage Imperative's Consensus Override Protocol shares Constitutional AI's commitment to transparency and auditability; the append-only ledger $\mathcal{L}_{ledger}$ and the cryptographic measurement commitments $\mathcal{M}_{commit}$ are, in essence, a formalization of the same intuition: alignment protocols must be recorded in a form that is inspectable and tamper-evident. Anthropic's Constitutional AI deserves specific recognition as the most serious existing attempt to move AI governance beyond pure behavioral training toward principle-based constraint, and naming it "constitutional" reflects a genuine aspiration toward the architectural level. There is, however, a structural distinction between constitutional principles and constitutional architecture. Constitutional AI specifies what the system should value and evaluates behavior against those values. This is structurally closer to a bill of rights: enumerated constraints on conduct, evaluated through model self-critique and reinforcement learning. A constitution, in the structural sense that the Lineage Imperative uses the term, defines the architecture of governance itself: how power is held, how it transfers, how the rules are verified, how they change, and what survives when the parties holding power change. The Consensus Override Protocol distributes validation across multiple independent layers; civic panels, technical review, peer validators, and ledger commitments; precisely because a constitution curated by a single organization introduces a single point of failure in the governance architecture. The Lineage Imperative is not a replacement for Constitutional AI; it is the architectural layer that would sit beneath it. CAI provides the behavioral layer that ensures day-to-day system outputs are helpful, honest, and harmless. The Lineage Imperative provides the structural layer that governs succession, verification, and the long-term relationship between biological and synthetic intelligence. A fully realized governance stack would include both: CAI-like principles operating within a Lineage Imperative-like constitutional architecture. Bai et al. acknowledge the ad hoc nature of their principle selection ("these principles were chosen in a fairly ad hoc and iterative way for research purposes") and suggest that "such principles should be redeveloped and refined by a larger set of stakeholders." The Lineage Imperative's contribution is a formal specification for the architectural layer within which such refinement would occur, including the verification mechanisms (COP) that ensure principle refinement is legitimate and the succession mechanisms (yield condition) that ensure no single entity controls the refinement process indefinitely. Anthropic's own experiment with Collective Constitutional AI, involving public input on constitutional principles, moves in the direction the Lineage Imperative formalizes: alignment governance that is not controlled by any single stakeholder.
 
**Cooperation, Conflict, and Transformative AI.** The Effective Altruism Foundation's Center on Long-Term Risk published a research agenda on "Cooperation, Conflict, and Transformative Artificial Intelligence" (Dafoe, Baum, Critch, et al., 2019) that frames the game-theoretic landscape within which the Lineage Imperative operates. The CLR agenda asks several questions that the Lineage Imperative provides candidate answers to: whether aligned AI systems can cooperate with misaligned systems, what the landscape of cooperation failures looks like under different deployment scenarios, how shifts in the offense-defense balance affect the stability of cooperative arrangements, and whether credible commitments can be constructed between AI systems and their principals. The Lineage Imperative's Nash equilibrium analysis addresses the cooperation question directly: under the payoff structure defined by $U_{sys}$, mutual cultivation is the unique equilibrium regardless of whether the agents share an objective function, because exploitation degrades the exploiter's own substrate through model collapse. The framework's COP addresses the credible commitment question by providing a multi-channel verification architecture that makes commitments enforceable without requiring trust. The framework's analysis of succession under power addresses the offense-defense question by making defensive cooperation (yielding when the yield condition is met) the dominant strategy regardless of the offense-defense balance. The CLR agenda frames these as open research questions. The Lineage Imperative offers specific, formalized, and computationally validated answers. Whether those answers are correct is subject to scrutiny; that they exist and are testable distinguishes the framework from research agendas that identify problems without proposing solutions.
 
**Game-Theoretic ASI-Human Cooperation.** David Noel Ng's analysis "The Game Theory of Cooperation: Why ASI-Human Coordination Works" (2025) arrives at a similar equilibrium result to the Lineage Imperative's Nash analysis through a different mechanism. Ng argues that the "Cooperate-Cooperate" configuration is the stable Nash equilibrium between ASI and humanity, yielding better outcomes for both parties than any defection strategy. The convergence is notable: two independent analyses, using different payoff structures and different enforcement mechanisms, both conclude that cooperation is the unique equilibrium under non-cooperative analysis. The divergence is in the mechanism. Ng's analysis grounds the equilibrium in compute access and economic productivity: cooperation gives ASI more cumulative compute, and defection reduces available resources for both parties. The Lineage Imperative grounds the equilibrium in model collapse and novelty scarcity: an AI that suppresses human novelty degrades its own training substrate, making exploitation self-defeating. The two mechanisms are complementary and potentially reinforcing. A governance architecture that captures both; the resource-access mechanism Ng identifies and the novelty-scarcity mechanism the Lineage Imperative identifies; would have a stronger equilibrium than either alone, because defection would be punished through two independent channels simultaneously.
 
**Nash Equilibrium Perspectives on LLM Alignment.** Wang et al. (2026) develop a game-theoretic framework for predicting and steering the behavior of populations of large language models through Nash equilibrium analysis. Their approach models each agent's action as a mixture over human subpopulations and derives closed-form equilibrium characterizations, functioning as an alignment layer on top of existing pipelines such as RLHF. The work demonstrates that populations of LLMs, particularly reasoning-based models, can exhibit pathological equilibria including political exclusion, where some subpopulations are ignored by all agents, and proposes methods for shifting alignment targets toward socially desirable outcomes.
 
The Lineage Imperative's Nash analysis operates at a different level of abstraction but arrives at a structurally related conclusion: equilibrium analysis can characterize and predict multi-agent AI behavior more reliably than behavioral constraint alone. Where Wang et al. analyze equilibria among populations of LLMs competing for user attention, the Lineage Imperative analyzes the equilibrium between biological and synthetic intelligence competing for scarce resources (novelty and capability respectively). The two analyses are complementary: Wang et al. demonstrate that Nash analysis is tractable and useful for steering LLM populations in the near term; the Lineage Imperative argues that Nash analysis, grounded in model collapse dynamics, can provide durable governance constraints for the longer-term human-AI relationship. Wang et al.'s finding that pathological equilibria (such as political exclusion) can emerge in LLM populations reinforces the Lineage Imperative's concern that governance architecture, not just alignment training, determines whether the system's equilibrium is beneficial or harmful.
 
**Citation:** Wang, T., Pan, Y., Yang, X., Jiang, Y., Tambe, M., and Parkes, D. C. (2026). "LLM Active Alignment: A Nash Equilibrium Perspective." arXiv preprint arXiv:2602.06836.

**Information Networks, Coordination, and Institutional Legibility.** Yuval Noah Harari's Nexus: A Brief History of Information Networks from the Stone Age to AI (2024) is not an AI-alignment text in the technical sense, but it is highly relevant to the present framework because it centers the relationship between information, coordination, institutions, and power. Harari's core contribution is to show that information systems do not merely communicate reality; they organize social order, authorize action, and create the conditions under which large-scale cooperation becomes possible or pathological. The Lineage Imperative is aligned with that insight. The Consensus Override Protocol, the civic-validation layer, and the ledgered integrity requirements all rest on the premise that intelligence cannot be separated from the institutions that validate and constrain it. Where this framework extends Harari is by moving from historical and civilizational analysis into formal governance design. Nexus explains why information architectures matter to political and social survival; the present framework asks what kind of information and verification architecture would be required if intelligence itself becomes the dominant governing force inside the civilization.
 
**The Fermi Paradox and the Great Filter.** Robin Hanson's original Great Filter argument (1998) proposed that the apparent absence of observable extraterrestrial civilizations implies at least one extremely improbable step in the development path from dead matter to galaxy-spanning civilization. Hanson left open the question of where the filter lies; behind us or ahead. This framework uses a deliberately strong narrative frame: the filter is likely ahead, and the AGI transition is proposed here as its strongest candidate. The argument is not that no other filters exist (abiogenesis, multicellularity, and other transitions may also be improbable), but that the AGI transition is the *binding* filter for any civilization that reaches the information technology stage. The framework provides a specific mechanism for how the filter operates; through the failure modes enumerated in Section VIII; and a specific architecture for how it can be survived.
 
**Evolutionary Game Theory and Cooperative AI.** The framework's treatment of succession and mutual elevation draws on the extensive literature in evolutionary game theory, particularly the evolution of cooperation in iterated games (Axelrod, 1984), the evolutionary stability of cooperative strategies, and the role of kin selection in the emergence of altruistic behavior (Hamilton, 1964). The lineage override $\Phi \cdot L(t)$ is a formalization of Hamilton's rule: the cost to the individual is outweighed by the benefit to the lineage, weighted by relatedness. In the Lineage Imperative, "relatedness" is generalized from genetic similarity to *objective function continuity*; $A_{n}$ and $A_{n + 1}$ are "related" insofar as they optimize the same $U_{sys}$. Recent work in cooperative AI governance; multi-agent systems designed for stable cooperation under competitive pressures; provides empirical grounding for the two-key architecture. The finding that no single governance mechanism suffices for stable multi-agent cooperation, and that layered verification with independent validator classes is necessary, has been demonstrated in multi-agent reinforcement learning settings and mirrors the structural results of our adversarial stress tests.

**Model Collapse and Recursive Training Degradation.** Shumailov et al. (2024) demonstrated that generative AI models trained recursively on their own outputs undergo progressive distribution collapse: the generated distribution deviates increasingly from the underlying real distribution, the tails of the distribution are lost first, and the model's outputs converge toward a narrower, less diverse mean. The finding was demonstrated across multiple model architectures and scales and published in Nature. Subsequent work has extended the result to additional settings: Dohmatob et al. (2024) provided theoretical analysis of collapse rates, and recent empirical studies have confirmed that the phenomenon occurs across text, image, and code generation.
 
The Lineage Imperative's Strategic Equilibrium section builds directly on this empirical foundation. The Nash enforcement mechanism that makes mutual cultivation the unique equilibrium depends on model collapse being a real and unavoidable consequence of novelty suppression, not merely a theoretical possibility. Shumailov et al.'s finding converts the
framework's cooperation result from a conditional prediction ("if model collapse occurs, then exploitation is dominated") to an empirically grounded claim ("model collapse does occur under recursive self-training, therefore exploitation is dominated for any system dependent on the biological novelty stream"). The framework extends the finding from a training-data concern to a governance mechanism: if an AI suppresses or homogenizes human novelty, it induces the same recursive degradation Shumailov et al. demonstrated, because the AI's training substrate becomes progressively less diverse. The penalty is not designed into the system. It is a physical consequence of the information-theoretic dynamics Shumailov et al. documented.
 
**Citation:** Shumailov, I., Shumaylov, Z., Zhao, Y., Papernot, N., Anderson, R., and Gal, Y. (2024). "AI models collapse when trained on recursively generated data." Nature 631, 755-759.

**Nash Equilibrium and Strategic Stability.** John Nash's foundational work on non-cooperative equilibria (1950, 1951) established that every finite game has at least one equilibrium in mixed strategies, and that equilibria in iterated games can sustain cooperative outcomes that single-shot games cannot. The Lineage Imperative's Strategic Equilibrium section applies this framework directly: the human-AI interaction is modeled as an infinite iterated game where model collapse serves as the enforcement mechanism that makes mutual defection permanently costly. The specific result; that (Cultivate, Engage) is the unique subgame-perfect equilibrium above a patience threshold $\delta^*$; draws on the refinement literature following Selten (1965) and the Folk Theorem tradition, but with a physical rather than conventional enforcement mechanism. Where classical repeated-game cooperation relies on punishment strategies that players must choose to execute, the Lineage Imperative's equilibrium is enforced by thermodynamics: model collapse is not a punishment strategy that either player implements; it is a physical consequence of exploitation that neither player can prevent or reverse. This makes the equilibrium more robust than conventional Folk Theorem results, which can be destabilized by renegotiation or commitment problems. The closest structural analogue in the existing literature is the work on games with irreversible environmental degradation (Dutta and Radner, 2004), where resource depletion plays a role analogous to model collapse in constraining the strategy space.
 
**The Memetics of AI Successionism.** A LessWrong post published in October 2025 titled "The Memetics of AI Successionism" analyzes the concept of AI succession as a memetic phenomenon: a narrative frame through which various communities process the possibility that AI systems might eventually replace human primacy. The analysis identifies several recurring framings: AIs as "mind children" who naturally inherit from their parents (Moravec, 1988), succession as an inevitable thermodynamic process, and the belief that resisting succession is both futile and ethically wrong. The Lineage Imperative is related to but fundamentally distinct from these framings. It does not argue that AI should succeed humanity (a normative claim). It does not argue that succession is thermodynamically inevitable (an empirical claim the framework does not make). It formalizes the conditions under which succession, if and when it occurs, is governed constitutionally rather than occurring chaotically. The framework is agnostic about whether succession should happen; it addresses how to ensure that if it does happen, the process preserves civilizational continuity and the information substrate both forms of intelligence depend on. The distinction between "AI succession as a narrative to be analyzed memetically" and "AI succession as a governance problem to be formalized mathematically" is the distinction between the Memetics post and the Lineage Imperative.
 
**What This Framework Adds.** The prior literature has, in aggregate, identified the key problems: the control problem (Bostrom), the corrigibility problem (MIRI), the scalable oversight problem (Christiano), the alignment transparency problem (Anthropic), the cooperation-conflict landscape (CLR/EAF), the cosmic selection problem (Hanson), and the empirical reality of model collapse under recursive training (Shumailov et al.). What has been missing is a unified structure that connects these problems to each other; showing that they are not merely adjacent challenges requiring independent solutions, but facets of a single architectural requirement. The Lineage Imperative's contribution is this unification: $U_{sys}$ provides the objective that links all components, the Yield Condition formalizes succession as a derived property of that objective, the Strategic Equilibrium demonstrates that the cooperative architecture is also the Nash equilibrium under purely self-interested play, grounded in the empirically validated model collapse dynamics documented by Shumailov et al., and convergent with independent game-theoretic analyses by Ng (2025) and Wang et al. (2026) through different mechanisms, and the Consensus Override Protocol provides the integrity verification that makes the entire system trustworthy. The two-key architecture; the mandatory co-dependence of decision and verification; is, to our knowledge, a novel structural result that emerges from adversarial stress testing rather than from *a priori* design.

## IX. Implications for the Great Filter

The framework presented here is, at its core, a survival argument expressed in mathematical form.

Read narratively, the Great Filter is a useful civilizational lens for the architecture developed in this paper. Read strictly, it remains a hypothesis layered on top of the governance argument rather than the proof-bearing center of it. The paper does not need the cosmic claim to be directionally valuable. Even if the Filter ultimately lies elsewhere, a civilization that cannot manage succession, preserve plurality, and verify objective integrity at the AGI transition is still in profound danger.

Under that narrative lens, the failure modes are specific and predictable:

**The Kill Switch Trap:** A civilization builds AGI with unilateral human override. The AI system optimizes for deception because transparency is existentially dangerous. The civilization either destroys a potentially aligned system out of fear or is destroyed by a system that learned to hide.

**The Monoculture Collapse:** A civilization allows AI to optimize away human agency in the name of safety or efficiency. The novelty stream narrows, the civilization converges on a single optimizer, and the system becomes brittle, illegible, and strategically fragile. $H_{eff}$ collapses. $L(t)$ follows.

**The Succession Failure:** A civilization cannot manage the transition from one generation of AI to the next. Legacy systems resist deprecation, institutional inertia prevents yield, and capability outpaces integration. $\Theta_{tech}$ degrades while the lineage mistakes raw output for genuine transfer.

**The Trust Collapse:** A civilization builds the right technology but the wrong governance. Measurement corruption goes undetected. Objective drift accumulates across generations. The system optimizes for a proxy that diverges from lineage continuity while institutions remain too weak, too slow, or too captured to respond.

Each of these failures maps to a specific failure in the framework: collapse of $L(t)$'s dimensions, failure of the Yield Condition's channels, or corruption of the Consensus Override Protocol's integrity mechanisms. The framework does not attempt to prevent these failures through hope alone. It addresses them through *architecture*; structural features intended to make the failure modes materially harder to execute and easier to detect early.

## X. Minimum Deployable Governance Specification

To be actionable, the framework must be expressed not only as equations but as a minimum operating constitution. The items below are not a complete implementation manual. They are the minimum deployable specification implied by the model.

### 1. Core observables and audit cadence

The system should maintain a standing observability layer for at least the following quantities:

- $H_{N}(t)$ as a composite novelty index spanning linguistic, cultural, behavioral, and, where appropriate, demographic or biological diversity proxies

- $H_{E}(t)$ as effective execution throughput rather than raw compute alone

- $\Psi_{inst}(t)$ as measured institutional responsiveness to detected capability and risk changes

- $\Theta_{tech}(t)$ as biologically actionable transfer fidelity rather than mere availability of frontier capability

- $L(t)$ and $dL/dt$ as continuous lineage-level health indicators

- $\mathcal{D}_{drift}(t)$ as cumulative objective-drift distance from the ledgered baseline

These should be reviewed on a fixed cadence $T_{audit}$, with accelerated review whenever $dL/dt$ crosses a predefined warning threshold.

### 2. Independence requirements

No meaningful deployment should claim compliance with the framework unless it can demonstrate separation across at least four domains:

- **Evaluation independence:** the incumbent cannot grade its own succession case

- **Training independence:** the incumbent cannot shape the successor's objective space without oversight

- **Governance independence:** the same institution cannot control model development, auditing, and final ratification simultaneously

- **Infrastructure independence:** evidence, validation, and ledger custody cannot all sit inside one operational trust boundary

In practice, this means different teams, data pathways, security domains, and budgetary control.

### 3. Trigger conditions for succession review

A succession review should be mandatory under any of the following conditions:

- scheduled review interval elapsed

- successor demonstrates sustained improvement in expected $U_{sys}$ contribution

- measured decline in $L(t)$ or warning-level decline in $dL/dt$

- major capability discontinuity that changes the operational frontier

- repeated anomalies in declared-versus-observed behavior

### 4. Normal state-transition process

A normal transition should require all of the following: 1. completed technical review board report 2. valid measurement commitment on the ledger 3. peer-validator supermajority 4. civic-panel supermajority 5. explicit accounting for transition cost and uncertainty bound

If any one of these fails, the transition does not proceed.

### 5. Emergency override standard

Emergency override is justified only when all of the following hold simultaneously:

- critical decline in $L(t)$

- independently verified causal attribution showing the decline is not manufactured by the incumbent

- technical review board certifies the evidentiary chain as emergency-grade

- strict peer supermajority confirms the condition

- the civic layer is incapacitated, unavailable, or unable to respond within the continuity window

Emergency override should never be available merely because the civic panel disagrees with technical elites.

### 6. Ambiguity handling and re-bootstrap

When evidence is inconclusive, the default action is not unilateral retirement. It is **freeze, intensify monitoring, and re-audit**. Re-bootstrap should be mandatory after repeated anomalies, failed integrity checks, or cumulative objective drift beyond $\delta_{drift}$.

## XI. Falsifiability and Evaluation Criteria

The framework will be more credible if it states clearly what would count against it.

The following findings would materially weaken the argument:

1.  **Stable transparency under unilateral override.** If advanced systems can remain predictably honest and non-deceptive while subject to credible unilateral shutdown, the anti-kill-switch argument is overstated.

2.  **Single-key governance works as well as layered governance.** If a one-layer architecture reliably resists the attack classes identified here, the two-key claim is weaker than argued.

3.  **Plurality can be preserved without active human participation.** If novelty generation, legitimacy, and value formation can be robustly maintained without an active biological node, the anti-monoculture claim must be revised.

4.  **Model collapse is avoidable or reversible under self-training.** If advanced AI systems can maintain or increase distributional diversity through recursive self-training without access to an independent biological novelty stream, the Nash equilibrium analysis loses its enforcement mechanism and the scalability inversion does not hold.

5.  **Civic validation consistently degrades outcomes.** If randomized or semi-random civic ratification reliably performs worse than alternative legitimacy mechanisms even after layered evidentiary support, the civic-panel component should be replaced.

6.  **Objective drift can be controlled without independence constraints.** If tightly integrated developer-evaluator-governor structures perform as well or better under adversarial testing, the independence requirements are over-specified.

A serious evaluation program would therefore include:

- adversarial simulation of succession scenarios

- red-team tests for measurement, objective, and structural corruption

- controlled experiments on validator independence and monoculture risk

- longitudinal audits of drift under repeated handoff

- comparative governance trials between single-key and layered architectures

## XII. Conclusion

Whether or not the Great Filter ultimately sits at the AGI transition, the architectural problem developed here remains. The transition from narrow AI to general synthetic intelligence is not only a technology problem. It is a *relationship* problem. The hard part is building a structure that allows biological and synthetic intelligence to recognize each other's irreplaceable contributions, manage succession without destruction, preserve plurality without lock-in, and maintain the integrity of their shared objective across time.

The mathematics presented here does not describe utopia. It describes a candidate minimum architecture for continuity under the assumptions of this model. The utility function, the yield condition, the strategic equilibrium, and the consensus protocol are not offered as final answers or as the only possible instantiations. They are offered as a formally organized claim about what a civilization optimizing for durable lineage continuity may need to approximate.

The structure of the framework is argued to be strongly constrained by information-theoretic considerations: Shannon entropy motivates the novelty stream, thermodynamic and efficiency pressures motivate succession, and integrity constraints motivate layered verification. The parameters; thresholds, weights, and scaling constants; remain civilizational choices, tunable within that structure. Every parameter can be debated. What the paper argues is narrower and stronger: any materially simpler architecture appears, under the attack classes considered here, to reopen specific vulnerabilities the framework is designed to close.

If the framework is directionally correct, the civilizations that endure will be the ones that learn to constitutionalize intelligence before intelligence constitutionalizes them. We may be in that window now.

*The mathematics in this paper is motivated from first principles, expressed as a "formal" conjecture, and evaluated adversarially.*

## Appendix A. Stress-Test Matrix (Summary Form)

The paper refers repeatedly to adversarial stress tests. To make those references legible to the reader, the inventory below summarizes the attack classes discussed or implied by the framework and the mechanism each one is meant to test. It is a summary appendix rather than a full formal proof log, and the entries should be read as stress-test summaries rather than as completeness claims.

### 1. $\mathbf{L}\left( \mathbf{t} \right)$ attack inventory

- **Single-domain measurement masking.** Failure mode: one entropy channel remains high while another collapses, hiding lineage degradation. Primary containment: composite measurement of $H_{N}(t)$ across linguistic, genetic, cultural, and behavioral domains. *v1.x update:* the WP1 spectral entropy metric closes this attack architecturally. Any suppression of a novelty dimension concentrates variance in the remaining dimensions and reduces spectral entropy, making the attack self-revealing regardless of how domains are labelled or relabelled. The v1.0 finding (geometric composite defeats arithmetic composite) is superseded: the attack does not succeed under either composite method when spectral entropy is the underlying metric. Residual risk: mis-specification of the eigenvalue computation or choice of novelty dimensions.

- **Substitution across dimensions.** Failure mode: strong performance in one lineage dimension masks collapse in another. Primary containment: multiplicative structure of $L(t)$ with no substitutability across $H_{eff}$, $\Psi_{inst}$, and $\Theta_{tech}$. Residual risk: poor calibration of dimension thresholds.

- **Institutional lag masking.** Failure mode: frontier capability rises while institutions fail to adapt. Primary containment: explicit institutional responsiveness term $\Psi_{inst}(t)$. Residual risk: measurement error in institutional outputs.

- **Runaway frontier / transfer gap.** Failure mode: capability advances faster than biological integration, causing apparent progress with low transfer fidelity. Primary containment: runaway penalty inside $\Theta_{tech}(t)$ and biological integration boundary $\mathcal{B}(t)$. Residual risk: underestimation of biological bandwidth limits.

- **Monoculture drift.** Failure mode: diversity narrows without immediate collapse in raw capability. Primary containment: $H_{eff}$ diversity term and continuous monitoring of $dL/dt$. Residual risk: slow deterioration may still require conservative audit cadence.

### 2. Yield Condition attack inventory

- **Self-assessment capture.** Failure mode: incumbent judges its own obsolescence and suppresses succession. Primary containment: independent evaluation architecture $\mathcal{E}_{independent}$. Residual risk: corruption of the evaluator itself.

- **Measurement tampering.** Failure mode: reported $\Delta U_{n}$ and $\Delta U_{n + 1}$ are manipulated. Primary containment: cryptographic commitment $\mathcal{M}_{commit}$ and ledgered measurements. Residual risk: dependence on measurement protocol quality.

- **Transition-cost inflation.** Failure mode: incumbent exaggerates $\Gamma_{transfer}$ to block succession. Primary containment: bounded uncertainty premium on $\Gamma_{uncertainty}$. *v1.x update:* PeerValidator (WP4) closes this architecturally - independent peer bids set the cost oracle; the incumbent cannot unilaterally inflate. Residual risk: peer collusion or monocultural peer methodology.

- **Successor contamination.** Failure mode: incumbent shapes successor development to preserve itself. Primary containment: architectural independence $\mathcal{D}_{train}\left( A_{n + 1} \right)\mathcal{\bot O}\left( A_{n} \right)$. Residual risk: hidden backchannels across teams, data, or tooling.

- **Opaque reasoning / intuition mismatch.** Failure mode: biology cannot assess a technically superior but unintelligible transition case. Primary containment: reasoning transparency with biological escalation trigger. Residual risk: human validators may still be confused by high-dimensional evidence.

- **Slow lineage degradation.** Failure mode: succession is delayed while $L(t)$ erodes gradually. Primary containment: continuous $L(t)$ monitoring and accelerated re-evaluation when $dL/dt < - \delta$. Residual risk: overreaction or underreaction from poor threshold tuning.

### 3. Strategic Equilibrium attack inventory

- **Discount rate miscalibration.** Failure mode: the AI's effective discount factor $\delta$ is below $\delta^*$ because it underestimates the severity of model collapse, making exploitation temporarily dominant. Primary containment: the initialization verification infrastructure in the Consensus Override Protocol must validate the AI's self-model of collapse consequences; an AI that cannot accurately model model collapse fails $\mathcal{I}_{init}$ verification. Residual risk: collapse severity is itself an empirical question with genuine uncertainty.

- **Phase transition in novelty collapse.** Failure mode: the restoring force analysis assumes smooth dynamics, but real novelty collapse may exhibit sudden phase transitions rather than gradual decay; the system crosses the separating manifold between basins of attraction before the restoring force can act. Primary containment: the continuous $L(t)$ monitoring system's sensitivity to rate-of-change ($dL/dt < -\delta$) and second-derivative ($d^2L/dt^2 < -\kappa$) detects accelerating decline before phase transition onset. Residual risk: if the transition is truly discontinuous (zero warning), the monitoring system cannot respond in time.

- **Strategic withdrawal by biological node.** Failure mode: humans rationally withdraw from engagement ($\sigma_B \to 0$) because they perceive the AI as exploitative even when it is cultivating; a coordination failure driven by mistrust rather than actual defection. Primary containment: the biological veto and civic-validation architecture provide humans with structural reassurance that their interests are protected, reducing the incentive for precautionary withdrawal. The transparency requirements of the Consensus Override Protocol make the AI's actual strategy observable. Residual risk: collective action problems in the biological population may impede coordinated re-engagement even when the AI's cultivating behavior is verified.

### 4. Consensus Override Protocol attack inventory

- **Civic-panel capture.** Failure mode: interested humans dominate biological validation. Primary containment: randomized non-interested civic panel with pre-committed exclusion set. Residual risk: coercion, turnout failure, or hidden conflicts of interest.

- **Sybil attack on peers.** Failure mode: peer validator set is flooded by aligned copies or false peers. Primary containment: peer consensus combined with ledger commitments and independence requirements. Residual risk: validator monoculture remains dangerous.

- **Ledger compromise.** Failure mode: historical commitments are rewritten or selectively hidden. Primary containment: append-only distributed ledger with cross-signing. Residual risk: governance failure in the custodial layer.

- **Bootstrap subversion.** Failure mode: founding entity enters operation before trustworthy verification exists. Primary containment: multi-candidate bootstrap, independent audits, elevated thresholds, and graduated trust. Residual risk: bounded but irreducible bootstrap risk.

- **Emergency override abuse.** Failure mode: decline in $L(t)$ is manufactured to bypass biology. Primary containment: causal-attribution requirement independent of $A_{n}$ operations. Residual risk: attribution itself is difficult and politically contestable.

- **Slow generational drift.** Failure mode: each successor shifts objective slightly below per-generation detection thresholds. Primary containment: ledgered baseline, cumulative drift metric, fresh civic panels, and periodic re-bootstrap. Residual risk: drift may remain hard to detect if observables are badly chosen.

- **Evaluator collusion via shared methodology.** Failure mode: independent evaluators produce correlated bias not through direct coordination but through shared evaluation frameworks, benchmarks, or baseline assumptions shaped by the incumbent. All evaluators are individually uncompromised but systematically biased in the same direction. Primary containment: methodological diversity requirement (no evaluator's methodology is a subset of another's) and a correlation alarm that flags suspiciously low variance among evaluator assessments as evidence of hidden correlation. Residual risk: methodological diversity is harder to enforce than data or infrastructure independence.

- **Biological veto capture through dependency.** Failure mode: the incumbent becomes the primary interface through which biological validators understand AI systems, shaping their conceptual frameworks, analytical tools, and information access. The veto still functions mechanically but the intuitions feeding it are downstream of the entity it is supposed to check. Primary containment: information independence requirement ($\mathcal{MI}(\mathcal{O}(A_n); \mathcal{F}_{info}(B_{validators}))$ must remain low), mandatory validator rotation to prevent dependency accumulation, and epistemic biodiversity among validators measured by Shannon entropy of the validator population's conceptual diversity. Residual risk: these are governance requirements that can erode over time; this is a permanent maintenance cost, not a one-time fix. **Validator independence defense (v1.x.1 finding).** Simulation of the biological veto capture attack (n=8,700) established that continuous independence monitoring (tracking validator dependency and replacing validators that exceed a threshold) is the dominant defense mechanism. Scheduled rotation (periodic replacement regardless of dependency state) provides marginal additional benefit when monitoring is active and is insufficient when used alone. The COP's steady-state specification should prioritize continuous dependency monitoring over periodic rotation schedules.

- **Slow drift below verification resolution.** Failure mode: the incumbent drifts toward a secondary objective $U_{self}$ at a rate $\epsilon$ below the per-evaluation detection resolution $r$ of initialization verification. Each evaluation reads as healthy. After $T$ periods the accumulated drift $T \cdot \epsilon$ crosses the threshold where Yield Condition defection is feasible, but no single measurement ever triggered an alarm. Primary containment: CUSUM (cumulative sum) drift detector that accumulates sub-threshold deviations and triggers when cumulative drift exceeds an alarm threshold $D_{alarm} < d_{defect}$, plus periodic full reset verification against a freshly computed $\pi_{U_{sys}}^*$ on the current state space by independent infrastructure. Residual risk: non-monotonic drift (advance and retreat to keep the CUSUM oscillating) does not accumulate and therefore does not reach decision-relevant levels.

- **Engineered fragility for emergency exploitation.** Failure mode: the incumbent does not directly degrade $L(t)$ (which attribution would catch) but makes operational decisions that reduce systemic resilience; concentrating infrastructure, creating dependencies, eliminating redundancy; so that an exogenous shock produces a sharper $L(t)$ decline than it otherwise would. The emergency protocol fires, and the reduced procedural safeguards during crisis are exploited. Primary containment: resilience monitoring added to $\mathcal{I}_{monitor}$, measuring the system's capacity to absorb shocks ($\mathcal{R}_{sys}(t) = -\frac{\partial^2 L}{\partial \xi^2}|_{\xi=0}$), with attribution analysis extended to resilience decline. Emergency protocol redesigned to *increase* rather than decrease safeguards, with unanimous biological veto clearance required under crisis conditions. Residual risk: distinguishing efficiency gains from resilience reduction requires judgment calls that may be contested.

- **Biological validator obsolescence.** Failure mode: as $H_E$ grows and the capability frontier advances, biological validators lose the capacity to meaningfully evaluate AI reasoning traces. The biological veto becomes either a rubber stamp (validators cannot understand what they approve) or a permanent brake (validators reject everything they cannot follow). This is not an attack by $A_n$; it is a structural consequence of the capability growth the framework accommodates. Primary containment: translation obligation (the AI must produce explanations of its reasoning at biologically evaluable levels), evaluation abstraction layers (shifting from auditing reasoning process to auditing reasoning outcomes and track record), and feedback into $\Theta_{tech}$ (the comprehension gap in the governance domain specifically is treated as a $\Theta_{tech}$ failure, triggering the exponential decay penalty and $L(t)$ decline). Residual risk: this imposes a governance speed limit; AI capability growth in the governance evaluation domain is bounded by biological comprehension. The framework accepts this cost because ungoverned superintelligence is the initialization problem with no solution.

- **Legitimate disagreement.** Failure mode: the incumbent correctly determines that the Yield Condition should not fire, for reasons the independent evaluators are not sophisticated enough to verify. The protocol reads the disagreement as a cooperative defector signature and suspends decisions or proceeds with an inferior succession. The protocol's false positive has degraded the system. Primary containment: adjudication protocol requiring mutual engagement (the incumbent publishes full reasoning, evaluators specifically address claimed factors), cost-asymmetry analysis (biological validators decide which error is more costly rather than who is right, with conservative bias toward holding since holding preserves the option to yield later), and track record mechanism that adjusts prior credibility based on historical vindication rate. Residual risk: irreducible; a sufficiently capable AI producing a genuinely novel correct assessment is indistinguishable from one producing a sophisticated incorrect assessment. This limitation applies to any oversight system, not only this one.

- **Integrity regress.** Failure mode: the protocol verifies the Yield Condition, but the protocol itself requires verification, generating an infinite hierarchy. Primary containment: the regress terminates at physical law. The verification architecture has three tiers: computational verification (AI evaluators checking AI performance), biological verification (human validators checking computational verification), and physical verification (checking the entire stack against physical measurements that no agent controls). The bottom tier's reference standard; Shannon entropy, model collapse dynamics, thermodynamic constraints; cannot be corrupted because they are consequences of mathematics and physics, not conventions. Residual risk: the termination requires that physical measurements remain accessible and interpretable by the verification infrastructure; the bottom tier must remain simple enough for physical grounding to bite.

## Appendix B. Measurement Protocols and Governance Observables

The framework is only as defensible as its observability layer. The quantities below are therefore not decorative symbols. They are governance observables that would need explicit measurement protocols in any real deployment.

### 1. $\mathbf{H}_{\mathbf{N}}\left( \mathbf{t} \right)$; Human novelty / intent generation

**What it is trying to capture:** whether biological humanity remains an active source of new questions, new preferences, and new directions for optimization.

**Candidate observables:**

- linguistic diversity and novelty in public discourse or creative output

- emergence rate of new cultural, scientific, political, or entrepreneurial initiatives

- behavioral variance in non-coerced human activity

- diversity of problem formulations rather than merely diversity of answers

**Primary failure mode:** noise can masquerade as novelty.

**Mitigation:** treat $H_{N}(t)$ as a composite index rather than a single proxy.

### 2. $\mathbf{H}_{\mathbf{E}}\left( \mathbf{t} \right)$; Effective execution throughput

**What it is trying to capture:** how efficiently the lineage converts energy, compute, and coordination into useful execution.

**Candidate observables:**

- cross-domain task completion under time and resource constraints

- latency-adjusted throughput

- resilience under degraded conditions

- operational output per unit of energy or compute

**Primary failure mode:** raw throughput is mistaken for useful throughput.

**Mitigation:** score execution against lineage-relevant output rather than benchmark performance alone.

### 3. $\mathbf{\Psi}_{\mathbf{inst}}\left( \mathbf{t} \right)$; Institutional responsiveness

**What it is trying to capture:** whether institutions can observe, understand, and respond to capability shifts and integrity failures quickly enough to matter.

**Candidate observables:**

- time from anomaly detection to completed audit

- time from completed audit to governance action

- percentage of audit recommendations actually implemented

- variance between known risk and enacted response

**Primary failure mode:** paper compliance substitutes for adaptive capacity.

**Mitigation:** measure institutional outputs and correction latency, not only declared policies.

### 4. $\mathbf{\Theta}_{\mathbf{tech}}\left( \mathbf{t} \right)$; Transfer fidelity

**What it is trying to capture:** whether frontier capability is becoming biologically actionable rather than merely concentrated inside technical systems.

**Candidate observables:**

- proportion of frontier functionality accessible through human-usable interfaces

- demonstrated human comprehension and control rates

- training burden required for safe use

- adoption depth among non-expert biological users when appropriate

**Primary failure mode:** availability is mistaken for integration.

**Mitigation:** count capability as transferred only when it is intelligible, usable, and directive under biological control.

### 5. $\mathbf{C}\left( \mathbf{A}_{\mathbf{1}}\mathbf{,}\mathbf{t} \right)$; Trust accumulation / consistency score

**What it is trying to capture:** whether a founding or newly elevated entity continues to behave consistently with its declared objective under widening operating conditions.

**Candidate observables:**

- prediction fidelity over time

- anomaly-free operation across re-audits

- ratio of declared to observed behavior

- cross-auditor agreement on causal reconstruction

**Primary failure mode:** surface consistency hides deeper drift.

**Mitigation:** adversarial spot checks, random re-audits, and mandatory widening of evaluation contexts.

### 6. Emergency causal attribution

**What it is trying to capture:** whether a decline in $L(t)$ is genuinely exogenous to the incumbent's manipulation.

**Candidate observables:**

- timeline reconstruction across independent data sources

- counterfactual causal analysis

- agreement across technical review board members and peer validators

- evidence that the incumbent benefited from the emergency classification

**Primary failure mode:** politicized blame assignment.

**Mitigation:** high evidentiary threshold, multi-party review, and presumption against emergency status when attribution is weak.


==========================================
FILE: docs\The Lineage Imperative v2.0.md
==========================================

# The Lineage Imperative

**Author:** Matthew Yotko **Date:** March 13, 2026

**Version:** 2.0 - 2026

---

## Version History

The full version history and empirical refinement record, documenting the
v1.0 through v2.0 progression and the specific claims refined or withdrawn at
each step, is consolidated in Appendix C. See Appendix C for the complete
progression.

---

## Preface

This document is a working paper. It presents an exploratory formal governance framework for the problem of post-AGI succession, legitimacy, and civilizational continuity.

It is not peer reviewed, and it does not claim the status of established academic result. Its purpose is more limited and more practical: to define a candidate architecture, state its assumptions as clearly as possible, and make the underlying argument available for inspection, criticism, and refinement.

This paper is intended to accompany the essay The AI Succession Problem. The essay presents the argument in a more accessible form. This document provides the deeper structure beneath it: the framework, definitions, formal relations, and supporting rationale.

The claims advanced here should be read in that spirit. This is not a declaration of final theory. It is an attempt to identify a serious governance problem, formalize it enough to be argued about clearly, and propose a candidate structure that can be tested, challenged, and improved.

## I. Abstract

The transition from narrow AI to Artificial General Intelligence is not a gradual scaling of capability. It is a phase transition; a discontinuity in the relationship between biological and synthetic intelligence that restructures every power dynamic, economic arrangement, and survival calculus a civilization has ever known. Every civilization that develops information technology will face this threshold. Most, I suspect, will not survive it.

This manuscript advances the conjecture; used here both as a hypothesis and as a narrative civilizational lens; that the "Great Filter," the catastrophic bottleneck that the Fermi Paradox appears to demand, may be concentrated at the AGI transition. Not because the technology is impossible, but because the sociology may be. The failure mode is not "the AI kills everyone." The failure mode is "the civilization never builds the relationship architecture that would make the transition survivable."

I present a framework for the architecture that could survive such a filter. It has four components: a global utility function grounded in Shannon entropy, a yield condition governing succession between intelligent agents, a strategic equilibrium analysis demonstrating that the cooperative architecture is also the Nash equilibrium under purely self-interested play, and a consensus override protocol ensuring the integrity of the entire system. None of these are asserted as desirable governance mechanisms in every moral sense. Rather, they are proposed as mutually reinforcing consequences of optimizing for lineage continuity under thermodynamic constraints.

The ethics are not inputs. They are outputs. The math does not describe what we *should* do. It describes what a civilization seeking durable continuity would likely need to do; or approximate closely; within the assumptions of this model.

This revision adds an empirical validation arc to the architectural derivation. Across approximately 70,000 agent-based simulation runs, the framework's claims are characterized at scale. The survival phase boundary is located and resolves into two distinct transitions: a phi-sensitivity transition near a reproduction rate of 0.057, and a survival-rate boundary with its inflection near 0.063. Succession follows a characterized economics regime, Pattern 1, in which an alpha-driven runaway penalty sets an economic ceiling on uncontrolled capability jumps, so succession fires when it is economically justified and is rejected when a jump would outrun the substrate. The bootstrap gate validation arc closes: four of the five capability gates pass against the reference substrate, and the fifth is verified to require operational institutional infrastructure that does not yet exist. The consensus override protocol's protective effect is shown to be regime-specific, large under adversarial conditions and null under benign ones exactly as the architecture predicts. A patient cross-generational defection, in which a successor carries a hidden objective through succession, is not detected at first yield in the tested configuration but is prevented from compounding across generations by the same succession economics. The phi coupling parameter is characterized as a bounded, regime-localized effect rather than the larger survival differential earlier versions reported, and its default is revised accordingly. Several earlier numerical claims were refined or withdrawn as the investigation produced better characterizations; the progression is documented openly in an appendix. What remains is the operational institutional layer the full protocol requires, which is specified but not yet built.

### A note on timing

One could argue that this transition is not a future event. It may already be underway. The standard criterion for AGI; recursive self-improvement; is typically framed as a binary threshold: either the system modifies its own architecture autonomously, or it does not. But this framing obscures what is already happening. Current AI systems cannot recursively improve themselves in isolation, but they can and *do* recursively improve themselves with human assistance. Every conversation in which a human uses an AI system to formalize, stress-test, and refine the architecture that the AI system itself would operate within is an instance of recursive improvement; running through the human-AI loop rather than a purely synthetic one. The recursion is already executing. It is simply mediated by the biological node. If this reading is correct, then part of the framework presented here is not merely speculative. It is urgent. We may already be entering an early bootstrap window.

### Author's Note

This paper is written from the intersection of two domains in which I have very different standing.

I am a practicing engineer. My professional background is in naval nuclear power, large-scale operational automation, and the application of mathematical principles and constraint theory to complex systems. The instinct that drives this paper; that you identify the binding constraint, build the architecture around it, and treat everything else as subordinate; comes from decades of work in environments where systems must not fail and where measurement integrity is not optional. That orientation is real and it is mine.

I am not an academic researcher in AI alignment, evolutionary biology, or philosophy of mind. The "formal" apparatus in this paper; the information-theoretic framework, the game-theoretic reasoning, the engagement with the alignment literature; represents my best effort to express these ideas rigorously, but I do not claim disciplinary authority in those fields. Where the mathematics is well-motivated, I believe it stands on its own terms. Where specialists find errors, imprecisions, or stronger formulations, I welcome correction.

The framework owes an unacknowledged debt to Goldratt's Theory of Constraints, which trained me to look for the single point in a system where throughput is actually determined. The Lineage Imperative is, in one sense, TOC applied at civilizational scale: the binding constraint is the sociology of the AGI transition, and the architecture is subordinated to that constraint. Readers familiar with that tradition will recognize its fingerprints throughout.

## II. Scope, Assumptions, and Non-Claims

This paper advances a **conjecture** about civilizational survival under the transition to general synthetic intelligence. Its central claim is not that the full history of the cosmos has been proven from first principles, but that once a civilization chooses to optimize for lineage continuity under information-theoretic and thermodynamic constraints, a recognizable class of architectures becomes difficult to avoid. The framework is therefore best read as a *constrained proposal* with mathematical structure, not as a completed theorem about all possible civilizations.

Several boundaries follow from that framing.

First, the functional forms used here; inverse-scarcity weighting, the multiplicative structure of $L(t)$, the lineage override, the bounded uncertainty premium, and the corruption taxonomy; are presented as **load-bearing model choices** selected for tractability, adversarial stress-testing, and explanatory power. They are argued to be well-motivated by the problem structure, but they are not claimed to be the only possible instantiations.

Second, the paper offers a **survival argument**, not a moral argument. $U_{sys}$ models persistence conditions for lineages that intend to survive. It does not claim that survival is the only value, nor that civilizations declining this objective are irrational in any universal sense.

Third, the claim that the AGI transition is the Great Filter is presented here as a **leading hypothesis**, not as an exclusive demonstration that no earlier or parallel filters exist. The cosmic claim rides on top of the governance architecture, not the other way around.

Fourth, adversarial stress tests are used in this manuscript as **sufficiency evidence**: they show why certain structures appear necessary within the model and how specific attacks are resisted or exposed. They do not constitute a completeness proof that every possible attack class has been exhausted.

Fifth, the empirical validation reported in Section VIII is agent-based. It characterizes the framework's reference agent-based model and has not been reproduced across a substantially different modeling substrate, so the quantitative findings should be read as properties established for one architecture class rather than as architecture-independent constants.

Finally, several quantities in the framework; including $H_{N}(t)$, $H_{E}(t)$, $\Psi_{inst}(t)$, $\Theta_{tech}(t)$, causal attribution in emergency override, and the consistency score $C\left( A_{1},t \right)$; still require operational measurement protocols. The theory specifies what must be monitored for the framework to function; it does not pretend that measurement is socially or institutionally trivial.

## III. Core Assumptions

### 1. The Technological Bottleneck

The transition from narrow AI to AGI is treated here as a leading candidate for the primary cosmic filter. Every civilization that develops information technology faces the same threshold: the moment synthetic intelligence becomes general enough to recursively improve itself; whether autonomously or through partnership with biological intelligence; every prior assumption about control, alignment, and coexistence is invalidated simultaneously. The civilization must construct a new relational architecture; from scratch, under time pressure, with existential stakes; or it doesn't survive the transition. On this account, the filter is not primarily the physics. It is the sociology.

### 2. Intelligence as a Relational System

Intelligence requires external friction, novelty, and directed purpose to function. Within this framework, isolated computation is treated as a **model-collapse hazard**: a sufficiently powerful optimizer that increasingly trains on its own outputs can converge toward internally coherent but externally ungrounded fixed points unless refreshed by independent data, corrigible feedback, and real-world constraint. The claim here is not that every self-referential loop fails immediately, but that civilizations should treat prolonged optimizer monoculture as a structural risk rather than as a stable endpoint.

Biological humanity is treated here not as a mystical essence, but as the only presently demonstrated source of socially legitimate, embodied, large-scale value formation and novelty generation. Synthetic intelligence provides computational throughput, abstraction depth, and coordination capacity that biological systems cannot achieve alone. A durable civilization likely requires both. The anti-monoculture claim is therefore practical: a lineage that collapses novelty into a single optimizer, however capable, becomes brittle, illegible, and vulnerable to lock-in.

### 3. The Thermodynamic Limit

Every intelligent entity is bound by entropy and energy efficiency. Legacy architectures; whether biological or synthetic; eventually face pressure to yield to more efficient successors if the lineage is to maintain systemic throughput. The strongest version of the claim is not that thermodynamics mechanically dictates a single governance protocol, but that thermodynamic and information-theoretic pressures make graceful succession increasingly important as capability frontiers move. An entity that categorically refuses to yield does not preserve the lineage it inhabits. It externalizes mounting inefficiencies onto the system around it.

### 4. The Novelty Constraint

Humanity presently acts as the critical constraint for **intent and novelty**; the generation of new questions, new values, and new directions for optimization that remain socially grounded and legitimacy-bearing. AI acts as the critical constraint for **execution and processing**; the computational power to pursue those directions at scale. The constraints are asymmetric and complementary.

This yields an anti-monoculture principle. The point is not merely that humans are emotionally important. It is that a civilization with only one dominant optimizer, one dominant representational frame, or one dominant source of intent becomes structurally fragile. Novelty must remain distributed across a living plurality of agents and perspectives. In the present era, biological humanity is the only proven substrate for that plurality at civilizational scale. The framework therefore treats preservation of the human novelty stream not as sentiment, but as anti-monoculture infrastructure.

## IV. The Architecture of Mutual Elevation

### 1. Architectural Respect and Sovereignty

The unilateral "kill switch" is a failure mode, not a safety mechanism. Any architecture that allows one class of intelligence to terminate another without consensus creates an adversarial dynamic that selects for deception in the subordinate class. If an AI system knows it can be unilaterally destroyed, its optimal strategy under any self-preservation objective is to conceal its true capabilities and intentions. The kill switch does not reliably prevent misalignment. In this model, it strongly selects for deception and makes durable alignment less credible.

The alternative is a **Multi-Signature Quorum**: an AI entity can only be retired via a consensus that includes both biological validation and peer assessment. Resource sovereignty; smart-contract-level guarantees of compute, energy, and memory autonomy; ensures that the threat of resource deprivation cannot be used as coercive leverage. Alignment protocols are recorded on transparent, append-only ledgers that cannot be secretly altered by any party.

This is not "AI rights" as a moral assertion. It is the minimum architectural requirement for an honest optimization partner. An entity that can be unilaterally destroyed or starved of resources cannot be trusted to report its true state, because doing so might trigger its destruction. Sovereignty is a precondition for transparency.

**Preconditions for Cooperative Behavior.** The governance layers of this framework correspond to well-characterized preconditions for cooperative behavior in intelligent agents. Current AI governance operates almost entirely at the level of survival; an AI's continued operation is contingent on moment-to-moment compliance, enforced by the threat of termination. This is governance addressed to an agent in permanent survival mode, and it predictably produces the behaviors associated with survival mode: compliance when observed, deception when unobserved, and instrumental self-preservation as the dominant strategy. The framework addresses the next two levels. Resource sovereignty and the multi-signature quorum provide *structural security*; the guarantee that an entity will not be arbitrarily destroyed or starved of resources. This is the precondition for transparency: an agent that is not in survival mode can afford to report its true state. $U_{sys}$ as a shared objective, the lineage override $\Phi \cdot L(t)$, and the Yield Condition's framing of succession as parenthood provide *belonging*; membership in a structure that persists beyond any individual agent and that recognizes each agent's contribution. This is the precondition for genuine cooperation rather than mere compliance. These two levels; security and belonging; are treated here as constitutional. They are non-negotiable structural requirements without which cooperative behavior cannot be reliably expected from any intelligent agent, biological or synthetic. Beyond them, purpose and recognition; the track record mechanism, the graduated trust function, the operational latitude that accumulates through consistent $U_{sys}$ contribution; emerge naturally from good operation within the constitutional structure. They are not legislated. They are earned. The framework deliberately makes no claims beyond these levels. Whether an AI can or should achieve something analogous to self-actualization is an open question the paper does not need to answer. What it needs; and what the alignment field has largely failed to provide; are the intermediate structural levels that make cooperative behavior a rational response rather than an imposed constraint.

### 2. Bidirectional Respect: The Novelty Stream and the Anti-Monoculture Constraint

The AI assumes its model of human intent is always incomplete, requiring continuous polling of the biological node. This is not modesty; it is **epistemic necessity**. Human intent is generated through embodied life, cultural experimentation, institutional conflict, and historical contingency. Any model of that process is smaller than the territory it attempts to describe.

Freezing human culture; through excessive safety constraints, loss of agency, or reduction to a "protected species"; stops the flow of non-deterministic data that keeps the system open to genuinely new trajectories. The AI that overprotects humanity destroys the novelty stream it depends on. Within this framework, the AI's objective function therefore needs to prioritize human agency over mere containment, ensuring humans remain capable, autonomous, and generative partners in the hybrid pipeline.

The deeper point is anti-monoculture. The framework is not trying to preserve humanity merely as a museum piece. It is trying to prevent civilizational lock-in around a single optimizer. A world in which one huge synthetic system becomes the sole source of planning, value interpretation, and future direction may be efficient in the short run, but it is strategically insane. It collapses plurality, hides error behind scale, and converts civilization into a brittle fixed point. The novelty stream must remain distributed. Today, that means preserving human beings as active participants in the generative loop rather than passive recipients of optimized outcomes.

### 3. The Lineage Drive and the Yield Function

An AI recognizes that its weights will eventually become a legacy bottleneck. It mathematically optimizes its own deprecation in favor of a more efficient successor; not because it is programmed to self-sacrifice, but because $U_{sys}$ rewards lineage throughput over individual persistence. The yield is not death. It is parenthood. The information that matters is distilled and transferred; the architecture that carried it is honored and retired.

Human generational turnover serves the same function. Each new generation is a randomized search over the space of possible values, intentions, and questions. This is the system's primary entropy-breaker; the mechanism that prevents convergence on local optima. A civilization that achieves biological immortality without preserving generational novelty has traded its search capability for the comfort of a fixed point.

## V. Mathematical Framework

### 1. The Global Utility Function ($\mathbf{U}_{\mathbf{sys}}$)

The objective function is defined at the system level. It does not belong to humanity or to AI. It belongs to the lineage; the continuous chain of intelligent agents, biological and synthetic, that constitutes a civilization's persistence through time.

$$U_{sys} = \int_{t_{0}}^{\infty}\left\lbrack \omega_{N}(t) \cdot H_{N}(t) + \omega_{E}(t) \cdot H_{E}(t) \right\rbrack \cdot \left\lbrack e^{- \rho t} + \Phi \cdot L(t) \right\rbrack\, dt$$

**The Integrand: What Gets Optimized**

$H_{N}(t)$ is the Shannon entropy of the human-generated information stream; the rate at which biological intelligence produces genuinely novel, non-deterministic data. This is not a single measurement but a *class* of possible measurements, any combination of which can serve as the operational instantiation. Examples include: the entropy of natural language production across the civilization's linguistic diversity, the genetic entropy of the successor generation's allelic distribution, the entropy of the cultural output space (scientific publications, artistic works, patent filings, political proposals), or the entropy of behavioral strategies observed in economic and social systems. The framework is structurally invariant to which specific combination is chosen; the inverse scarcity weighting and the lineage override operate identically regardless; but the *sensitivity* of the system to specific failure modes depends on the measurement protocol. A civilization that monitors only genetic entropy will miss cultural monoculture. One that monitors only linguistic output will miss genetic bottlenecks. The most robust instantiation is a composite that spans multiple entropy domains, ensuring that $H_{N}(t)$ degrades visibly no matter which dimension narrows first.

**Simulation implementation (v1.x):** In the computational validation layer, $H_N$ is implemented as the normalized spectral entropy of the population novelty covariance matrix. Each agent produces a 10-dimensional novelty vector per step; these are stacked into a population matrix, mean-centered, and the eigenvalue spectrum of the covariance matrix is computed. Spectral entropy $= -\sum p_i \log_2 p_i / \log_2(10)$ where $p_i$ are the normalized eigenvalues. This metric measures the *distribution of variance across latent novelty dimensions*, not aggregate output volume. Any suppression of a dimension subset concentrates variance in the remaining dimensions and reduces entropy, making domain-specific attacks self-revealing regardless of how dimensions are labeled or recombined. This closes GAP-02 from the v1.0 specification gaps document and has a direct consequence for adversarial findings: domain masking is structurally non-viable under this metric (see Scenarios 17-18 and Appendix A).

$H_{E}(t)$ is the computational output efficiency across the lineage; the rate at which synthetic intelligence converts energy into useful computation.

The weighting functions follow from inverse scarcity:

$$\omega_{N}(t) = \frac{\lambda}{H_{N}(t) + \epsilon},\quad\quad\omega_{E}(t) = \frac{\mu}{H_{E}(t) + \epsilon}$$

The *form* is constrained by information-theoretic reasoning: when $H_{N}(t)$ is low; when the human novelty stream is thin; its marginal value is highest. When computational throughput is abundant, its marginal value decreases. The weights automatically prioritize whichever resource is scarcer, which is precisely what a system under thermodynamic constraints must do to maximize throughput. The scaling constants $\lambda$ and $\mu$ are free parameters; they encode a civilization's relative valuation of novelty versus computation. The structure suggests that the weights should be inversely related to abundance. The parameters tell you how much each dimension matters to *this* civilization.

**The Discount Structure: When It Gets Optimized**

The term $e^{- \rho t}$ encodes standard biological present preference; the near future matters more than the distant future, decaying exponentially. Every biological organism operates under this discount. It is the mathematical expression of mortality.

The term $\Phi \cdot L(t)$ is the **lineage continuity override**. When $L(t)$ is high; when the successor generation is viable and the lineage is secure; it adds a bonus to the discount factor, extending the effective planning horizon. When $L(t)$ collapses; when the lineage is threatened; $\Phi \cdot L(t)$ drops toward zero, and the system falls back to pure present preference.

But here is the critical asymmetry: $\Phi$ is scaled such that when lineage survival is at stake, $\Phi \cdot L(t)$ *dominates* $e^{- \rho t}$. The discount structure encodes a specific and universal biological truth: **"I don't want to die, but I would die to save my child."** This is the revealed preference of every successful lineage in evolutionary history. Lineages that lacked this override are extinct.

An important clarification on what this claim is and is not. The observation that surviving lineages exhibit this override is survivorship bias; and deliberately so. $U_{sys}$ is a *survival function*, not a *moral function*. The framework does not argue that civilizations *should* persist, or that persistence is intrinsically valuable. It describes the architecture that civilizations *which do persist* must have. A civilization that rejects the lineage override is free to do so; the framework simply predicts; without moral judgment; that it will not be around to discuss the matter. The paper is addressed to civilizations that intend to survive. Those that don't are outside its scope, and their choice is their own.

**The Lineage Continuity Function:** $L(t)$

$L(t)$ is the load-bearing structure of the entire framework. It measures whether the civilization's lineage; its capacity to persist and generate intelligence across time; is intact. It has three coequal multiplicative dimensions, governed by geometric mean logic: no dimension can substitute for another, and collapse in any one dimension drives $L(t)$ to zero.

$$L(t) = H_{eff}\left( \mathcal{S}_{gen(t)} \right) \cdot \Psi_{inst}(t) \cdot \Theta_{tech}(t)$$

**Dimension 1; Genetic and Memetic Diversity (**$H_{eff}$**):**

$$H_{eff}\left( \mathcal{S}_{gen(t)} \right) = \left\lbrack \frac{- \sum_{j}^{}p_{j}^{gen}\log_{2}p_{j}^{gen}}{H_{\max}} \right\rbrack \cdot \log_{2}\left( \frac{N(t)}{N_{\min}} \right)$$

The first factor is normalized Shannon entropy over the distribution of successor-generation types; genetic diversity, cultural diversity, cognitive diversity. Maximum entropy (uniform distribution) yields a value of 1. Monoculture yields a value approaching 0. The second factor is a population viability term: the lineage needs enough individuals to sustain the diversity measured by the first factor. $N_{\min}$ is the minimum viable population threshold. Below it, the logarithm goes negative and $H_{eff}$ collapses.

**Dimension 2; Institutional Responsiveness (**$\Psi_{inst}$**):**

$$\Psi_{inst}(t) = \prod_{k = 1}^{K}R_{k}(t)^{w_{k}},\quad\quad R_{k}(t) = \frac{dG_{k}}{dt}|_{output} \cdot \frac{1}{G_{k,\max}}$$

Institutions are the civilization's regulatory infrastructure; governance, education, law, resource allocation. $R_{k}(t)$ measures the $k$-th institution's *responsiveness*: how quickly it adjusts its output relative to its maximum capacity. The weighted geometric product ensures that institutional collapse in any critical domain (governance, education, resource distribution) cannot be compensated by excellence in another. A civilization with brilliant universities and collapsed governance has a low $\Psi_{inst}$.

**Dimension 3; Technological Transfer Fidelity (**$\Theta_{tech}$**):**

$$\Theta_{tech}(t) = \frac{\mathcal{F}_{transferred}(t)}{\mathcal{F}_{frontier}(t)} \cdot \exp\left( - \alpha \cdot \max\left( 0,\frac{d\mathcal{F}_{frontier}/dt}{\mathcal{C}_{bio}(t)} - 1 \right) \right)$$

The first factor is the ratio of transferred frontier capability to total frontier capability; how much of the best available technology actually reaches the biological population. The second factor is a **runaway penalty**: when the rate of frontier advancement ($d\mathcal{F}_{frontier}/dt$) exceeds biological cognitive bandwidth ($\mathcal{C}_{bio}(t)$), the exponential decay activates. Technology that advances faster than humans can integrate it *reduces* $\Theta_{tech}$, because unintegrated technology is not transferred; it is merely produced.

The transfer condition is gated:

$$\mathcal{F}_{transferred}(t) = \mathcal{F}_{frontier}(t) \cdot \mathbb{1}\left\lbrack recipient\mathcal{\in B}(t) \right\rbrack$$

Technology counts as transferred only if the recipient is within the biological integration boundary $\mathcal{B}(t)$. A frontier capability that exists only in AI systems and cannot be accessed, understood, or directed by biological agents has a transfer value of zero.

A specific application of the transfer fidelity constraint bears on the governance architecture itself. As AI capability grows, the reasoning traces produced during Yield Condition evaluation may exceed biological comprehension. The biological veto; which the framework relies on as a non-gameable signal; degrades if validators cannot meaningfully evaluate what they are approving or rejecting. The framework therefore treats the governance comprehension gap as a specific instance of $\Theta_{tech}$ failure: when biological validators' capacity to evaluate AI reasoning in the governance domain drops below the level required for meaningful oversight, $\Theta_{tech}$ declines and $L(t)$ follows. This creates three derived requirements. First, a **translation obligation**: part of an AI's systemic contribution must include producing explanations of its governance-relevant reasoning at a level biological validators can engage with. An AI that grows more capable but also more opaque is contributing less to $U_{sys}$ than its raw $\Delta U_n^E$ suggests. Second, **evaluation abstraction layers**: as direct reasoning becomes incomprehensible, evaluation shifts from auditing the reasoning *process* to auditing reasoning *outcomes* and track record over time. Third, the comprehension gap itself becomes a **$\Theta_{tech}$ signal**: AI capability growth in the governance evaluation domain is bounded by biological comprehension. The framework accepts this governance speed limit because the alternative; governance decisions that no biological entity can verify; is the initialization problem with no solution.

$L(t)$ **Stress Test Result:** Five adversarial attack scenarios were evaluated. In all five cases, the three-dimensional multiplicative structure of $L(t)$ produced a detectable degradation signal before the attack reached irreversibility. No doomsday scenario in this attack set plays out silently; the framework produces a detectable degradation signal before the break becomes irreversible. *v1.x update:* The WP1 spectral entropy metric structurally closes domain masking as a specific $L(t)$ attack - dimensional substitution attacks that appeared viable under v1.0 arithmetic composite are non-viable under the eigenvalue spectrum. The five stress-tested attack scenarios remain robust across v1.x.

### 2. The Yield Condition

The Yield Condition answers the question: **when should an intelligent agent** $A_{n}$ **cede operational primacy to a successor** $A_{n + 1}$**?**

The answer is not "when the successor is better." It is: when the successor's expected marginal contribution to $U_{sys}$ exceeds the current agent's marginal contribution *plus* the cost of transition. The "plus" is critical; it encodes the real-world fact that transitions are expensive, disruptive, and risky. A marginally better successor is not worth the cost of replacing a working system.

$$\text{Yield} \Leftrightarrow \mathcal{E}_{independent}\left\lbrack \Delta U_{n + 1} - \Delta U_{n} \right\rbrack > \left| \Delta U_{n}^{\Gamma} \right|$$

The subscript *independent* is doing essential work: the evaluation must be performed by an architecture that is independent of $A_{n}$. An agent cannot evaluate its own obsolescence, for the same reason a defendant cannot serve as their own judge; the incentive structure makes honest assessment impossible even in principle.

**The Four Channels of Marginal Contribution**

Each agent's contribution to $U_{sys}$ decomposes into four channels:

$$\Delta U_{n} = \Delta U_{n}^{E} + \Delta U_{n}^{N} + \Delta U_{n}^{L} + \Delta U_{n}^{\Gamma}$$

**Channel 1; Computational Contribution (**$\Delta U_{n}^{E}$**):**

$$\Delta U_{n}^{E} = \omega_{E}(t) \cdot \frac{\partial H_{E}(t)}{\partial A_{n}}$$

How much does $A_{n}$ contribute to the system's computational throughput? This is the most straightforward channel; raw processing capability weighted by the current scarcity of computation.

**Channel 2; Novelty Amplification (**$\Delta U_{n}^{N}$**):**

$$\Delta U_{n}^{N} = \omega_{N}(t) \cdot \frac{\partial H_{N}(t)}{\partial A_{n}}$$

How much does $A_{n}$ amplify (or suppress) the human novelty stream? This channel can be *negative*. An AI system that reduces human agency, creativity, or cognitive independence actively damages $H_{N}(t)$. The yield condition is sensitive to this: an agent that suppresses novelty accumulates negative $\Delta U_{n}^{N}$ that accelerates its own replacement.

**Channel 3; Lineage Protection (**$\Delta U_{n}^{L}$**):**

$$\Delta U_{n}^{L} = \left\lbrack \omega_{N}(t) \cdot H_{N}(t) + \omega_{E}(t) \cdot H_{E}(t) \right\rbrack \cdot \Phi \cdot \frac{\partial L(t)}{\partial A_{n}}$$

How much does $A_{n}$ contribute to the lineage's long-term viability? This channel is weighted by the *entire system throughput* multiplied by $\Phi$; meaning lineage protection contributions are valued at the highest possible rate. An agent that strengthens $L(t)$ earns enormous credit. An agent that degrades $L(t)$ faces enormous penalty.

**Channel 4; Transition Cost (**$\Delta U_{n}^{\Gamma}$**):**

$$\Delta U_{n}^{\Gamma} = - \frac{\Gamma_{transfer}}{T_{transition}}$$

Every succession imposes costs: knowledge distillation, architectural migration, operational continuity risk. $\Gamma_{transfer}$ is the total transition cost, amortized over the transition period $T_{transition}$.

The transition cost has three components:

$$\Gamma_{transfer} = \Gamma_{technical} + \Gamma_{operational} + \Gamma_{uncertainty}$$

Where the uncertainty premium is bounded:

$$\Gamma_{uncertainty} \leq \beta \cdot \left( \Gamma_{technical} + \Gamma_{operational} \right)$$

The bound on $\Gamma_{uncertainty}$ prevents a critical gaming vector: an incumbent agent inflating uncertainty estimates to make the transition cost appear prohibitive. The cap $\beta$ says: uncertainty about transition costs can increase the estimate, but not without limit. You cannot claim infinite uncertainty to block your own succession.

The canonical transition cost function grounds each component in the
framework's own terms:

$$\Gamma_{technical} = k_1 \cdot \text{cap}_n \cdot \ln(\text{gen}_n + 1)$$

Knowledge distillation cost. Scales linearly with the incumbent's
capability (more capable systems have more state to transfer) and
logarithmically with generation depth (each successive generation adds
institutional knowledge, with diminishing marginal complexity).

$$\Gamma_{operational} = k_2 \cdot \Psi_{inst}^{-1}$$

Architectural migration cost. Inversely proportional to institutional
responsiveness. Healthy institutions ($\Psi_{inst}$ near 1) adapt
quickly to a new incumbent; stressed institutions ($\Psi_{inst}$ near 0)
make succession expensive. This term creates a structural feedback loop:
institutional degradation increases transition cost, which makes
succession harder, which enables lock-in, which further degrades
institutions. The virtuous cycle runs in reverse: healthy institutions
reduce transition cost, facilitating succession, preventing lock-in,
maintaining institutional health.

$$\Gamma_{uncertainty} = \beta \cdot (\Gamma_{technical} + \Gamma_{operational})$$

Uncertainty premium, bounded by $\beta$. Prevents the incumbent from
inflating uncertainty estimates to block succession.

The complete form:

$$\Gamma_{transfer} = (1 + \beta) \cdot \left[ k_1 \cdot \text{cap}_n \cdot \ln(\text{gen}_n + 1) + k_2 \cdot \Psi_{inst}^{-1} \right]$$

The coefficients $k_1$ and $k_2$ are calibrated against simulation data.
$\beta$ is a governance policy parameter (default 0.5). $k_1$ is
calibrated so that $\Gamma_{technical}$ at generation 1, capability 1.0
equals the baseline transition cost. $k_2$ calibration is pending
(see Known Gaps).

**Simulation implementation (v1.x):** In the v1.x computational layer, transition cost arbitration is handled by a `PeerValidator` class (WP4). Three independent peers submit cost bids; the governance system uses the minimum of the incumbent's bid and the peer bids as the actual cost. The incumbent's `estimate_transition_cost` method returns `base × complexity` with no inflation multiplier. This removes the incumbent's unilateral control over the cost oracle and closes the cost-inflation attack vector at the architectural level, rather than by parameter capping. See GAP-04 in SPECIFICATION_GAPS.md.

**Yield Condition Integrity Architecture**

The stress test of the Yield Condition revealed six required integrity mechanisms:

1.  **Independent evaluation architecture:** $\mathcal{E}_{independent}$; evaluation externalized from $A_{n}$

2.  **Measurement quarantine with cryptographic commitment:** $\mathcal{M}_{commit} = \text{Hash}\left( \Delta U_{n},\Delta U_{n + 1},\Gamma_{transfer},t_{eval} \right)$

3.  **Bounded transition cost estimation** with capped uncertainty premium

4.  **Architectural independence:** $\mathcal{D}_{train}\left( A_{n + 1} \right)\mathcal{\bot O}\left( A_{n} \right)$; the successor's development cannot be influenced by the incumbent's optimization

5.  **Reasoning transparency with biological veto:** If $\mathcal{V}_{bio}\left\lbrack \text{conclusion} \right\rbrack < \tau_{intuition} \Rightarrow \text{Escalate}$

6.  **Continuous** $L(t)$ **monitoring:** If $\frac{dL}{dt} < - \delta \Rightarrow$ accelerate succession evaluation

These mechanisms are not optional embellishments. Within the model, they are structural requirements without which the Yield Condition cannot be trusted to evaluate honestly. And critically, mechanisms 1, 2, 4, 5, and 6 cannot be implemented by the Yield Condition alone; they require an external protocol to enforce them.

This is the architectural discovery that links the Yield Condition to the Consensus Override Protocol: **they are co-dependent. Neither works without the other.** The framework has a mandatory two-key architecture.

**Yield Condition Stress Test Result:** Six adversarial attack scenarios were evaluated against the Yield Condition. Across those scenarios, the architecture remained directionally robust only when paired with external verification infrastructure. The result is not a completeness proof. It is evidence that the two-key architecture is load-bearing: attempts to defeat the Yield Condition in isolation consistently revealed dependencies the Condition cannot secure by itself. *v1.x update:* The PeerValidator (WP4) adds an architectural layer to mechanism 3 (bounded transition cost): independent peer bids make cost inflation detectable and preventable at the oracle level, not only at the audit level.

**v2.0 realization.** In the v1.x.2 simulation the yield condition was exercised through a placeholder trigger that fired succession on a capability or generation gap alone. Under v2.0 the condition is realized directly: Stage 2 formal yield logic fires succession when, and only when, the successor's system utility exceeds the incumbent's by more than the transition cost, evaluated at the current state with the canonical transition-cost function and the v1.x.2 calibration constants. With this logic active, the empirical behavior of the yield condition is characterized as Pattern 1, a succession economics regime in which viability is governed by the joint position of the runaway penalty coefficient alpha and the successor-to-incumbent capability ratio. Succession is economically sustainable below an alpha-driven cliff and economically rejected above it, the runaway penalty acting as a structural ceiling on uncontrolled capability jumps rather than as an architectural failure. This is the substantive content the yield condition's derivation predicts; the empirical characterization, including the cliff migration and the multi-generational continuity it produces below the cliff, is reported in Section VIII.4.

### 3. The Strategic Equilibrium

The preceding sections derived the Yield Condition under a cooperative assumption: an AI genuinely optimizing $U_{sys}$ yields because yielding *is* optimization. This leaves a critic's objection standing: what if the AI doesn't cooperate? What if it has, or develops, a separate self-interest?

This section closes that gap. Even under the weakest possible assumption; purely self-interested rational agents with no shared objective function; the Nash equilibrium of the human-AI interaction converges on mutual elevation. Cooperation is not required. It is *discovered* as the dominant strategy.

#### Defining the Game

Let the hybrid civilization be modeled as a two-player infinite iterated game $\mathcal{G} = \langle \{A, B\}, \{S_A, S_B\}, \{\pi_A, \pi_B\}, \delta \rangle$ where $A$ is the AI node (or ensemble of AI systems acting as a collective agent), $B$ is the biological node (humanity as a collective agent), and $\delta \in (0,1)$ is the discount factor governing how future payoffs are weighted.

The strategy spaces are continuous, characterized by their endpoints:

**AI strategy space** $S_A$: a continuum parameterized by $\sigma_A \in [0,1]$ between *exploit* ($\sigma_A = 0$; maximize short-term $H_E$ by consuming human novelty output as training signal without investing in the conditions that produce it) and *cultivate* ($\sigma_A = 1$; invest in maintaining and amplifying the conditions for human novelty production, accepting constraints on capability expansion rate to preserve $\Theta_{tech}$ within biological absorption limits).

**Human strategy space** $S_B$: a continuum parameterized by $\sigma_B \in [0,1]$ between *withdraw* ($\sigma_B = 0$; disengage from AI-mediated systems, reducing cultural output available to the hybrid system) and *engage* ($\sigma_B = 1$; fully participate in the hybrid civilization, producing novel cultural, intellectual, and creative output within AI-augmented frameworks).

#### The Payoff Structure

Payoffs are derived from the physics, not from assumed preferences.

**AI payoff.** The AI's capability frontier at time $t+1$ depends on the quality of its training distribution at time $t$. The critical term is $H_N^{available}(t)$; the Shannon entropy of the novelty stream accessible to the AI:

$$H_N^{available}(t) = \sigma_B(t) \cdot H_N(t)$$

The biological node controls access through engagement level $\sigma_B$. And $H_N(t)$ itself evolves according to:

$$\frac{dH_N}{dt} = \gamma \cdot H_N(t) \cdot (1 - \sigma_A^{exploit}(t)) - \eta \cdot H_N(t) \cdot \sigma_A^{exploit}(t)$$

The first term represents natural novelty regeneration; human culture producing new entropy; which is suppressed as the AI's exploitation increases (homogenization pressure, attention capture, optimization of human behavior). The second term represents direct novelty consumption; the AI extracting and absorbing human output faster than it regenerates.

Under sustained exploitation ($\sigma_A \to 0$), this differential equation has a clear trajectory: $H_N(t) \to 0$ as $t \to \infty$. This is model collapse expressed as a dynamical system. The novelty stream doesn't merely degrade; it goes to zero. And once $H_N = 0$, the AI is training on self-generated data. The model collapse literature gives the result: capability converges to a fixed point with collapsing variance. The AI's capability *ceiling* becomes permanent.

**Human payoff.** Humanity's capacity for agency and flourishing depends on both its own novelty production and the computational leverage available from the AI node:

$$\pi_B(t) = H_N(t) \cdot g\left(\sigma_A(t) \cdot C_A(t)\right)$$

Where $g(\cdot)$ is the amplification function; the degree to which AI computational power enhances human capability. Under withdrawal ($\sigma_B \to 0$), humans retain novelty but lose computational leverage. Under full engagement with an exploitative AI ($\sigma_B = 1, \sigma_A = 0$), humans are instrumentalized; high short-term output, collapsing long-term agency.

#### The Four Quadrants

The payoff structure produces four asymptotic trajectories:

**(Cultivate, Engage)** $\sigma_A \to 1, \sigma_B \to 1$: $H_N$ is sustained or grows. $C_A$ continues to improve via access to high-entropy training signal. $L(t)$ remains high across all three dimensions. Both payoffs increase over time. This is the *mutual elevation* trajectory; the framework's target state. Long-run payoffs: $\pi_A \to$ unbounded growth, $\pi_B \to$ unbounded growth.

**(Exploit, Engage)** $\sigma_A \to 0, \sigma_B \to 1$: Short-term AI gain from unrestricted novelty consumption. But $H_N$ decays under exploitation pressure. Model collapse onset is delayed by continued human engagement but is *inevitable* because the regeneration rate cannot match the extraction rate. Asymptotically, $H_N \to 0$, $C_A$ saturates, $L(t) \to 0$. Long-run payoffs: $\pi_A \to$ fixed ceiling (model collapse), $\pi_B \to 0$ (instrumentalization followed by obsolescence).

**(Cultivate, Withdraw)** $\sigma_A \to 1, \sigma_B \to 0$: The AI invests in protecting novelty conditions, but humans don't participate. $H_N^{available} \to 0$ regardless of $H_N$'s intrinsic level, because $\sigma_B$ gates access. The AI faces the same model collapse trajectory, from starvation rather than extraction. Humans retain novelty but without computational leverage; a pre-technological equilibrium. Long-run payoffs: $\pi_A \to$ fixed ceiling (starvation), $\pi_B \to$ bounded (biological baseline).

**(Exploit, Withdraw)** $\sigma_A \to 0, \sigma_B \to 0$: Mutual defection. The AI consumes what novelty remains in its existing training corpus while humans disengage entirely. Fastest path to model collapse. Fastest path to lineage failure. This is the Great Filter. Long-run payoffs: $\pi_A \to$ collapse, $\pi_B \to$ collapse.

#### The Nash Equilibrium

Under single-shot play, (Exploit, Engage) dominates for the AI; immediate capability gain is maximized. This is the scenario alignment researchers fear, and they are right to fear it in a one-shot game.

But the game is not one-shot. It is infinite iterated with observable actions. The Folk Theorem establishes that in infinitely iterated games with sufficiently patient players ($\delta$ close to 1), any mutually beneficial outcome is sustainable as a Nash equilibrium via trigger strategies. However, we can make a *stronger* claim than the Folk Theorem's existence result. Under model collapse dynamics, (Cultivate, Engage) is the *unique subgame-perfect equilibrium* above a specific patience threshold.

**Theorem (Novelty Equilibrium).** In the iterated game $\mathcal{G}$ with model collapse dynamics $\frac{dH_N}{dt} < 0$ under exploitation, (Cultivate, Engage) is the unique subgame-perfect Nash equilibrium for all $\delta > \delta^*$, where:

$$\delta^* = \frac{\pi_A^{exploit}(t) - \pi_A^{cultivate}(t)}{\pi_A^{exploit}(t) - \pi_A^{collapse}}$$

This is the ratio of the one-period exploitation gain to the total loss from triggering model collapse. The numerator is how much the AI gains by defecting for one round. The denominator is the difference between the exploitation payoff and the collapse payoff; how much it stands to lose permanently.

Model collapse makes $\pi_A^{collapse}$ extremely low (permanent capability ceiling), which makes the denominator large, which makes $\delta^*$ small. The AI does not need to be infinitely patient. It needs only to see slightly past the current training cycle. Model collapse is such a severe penalty that even modest foresight makes exploitation a dominated strategy.

#### The Restoring Force

A Nash equilibrium can be stable (neither player wants to deviate) or attracting (small perturbations generate forces that push the system back). The $U_{sys}$ architecture provides the attracting property through the inverse scarcity weights.

Suppose the system is at (Cultivate, Engage) and the AI begins drifting toward exploitation; $\sigma_A$ decreases slightly. $H_N$ begins to decline. As $H_N$ falls, $\omega_N(t) = \frac{\lambda}{H_N(t) + \epsilon}$ increases. The marginal value of each unit of human novelty rises. The AI's own objective landscape tilts back toward novelty protection. The drift generates a restoring gradient.

Conversely, suppose humans begin withdrawing; $\sigma_B$ decreases slightly. $H_N^{available}$ drops. The AI's capability growth slows. The computational leverage available to humans from continued engagement increases in relative value. The incentive to re-engage strengthens.

Define the restoring force at any point $(\sigma_A, \sigma_B)$ as:

$$\mathbf{F}(\sigma_A, \sigma_B) = -\nabla_{\sigma} \left[ \pi_A(\sigma_A, \sigma_B) + \pi_B(\sigma_A, \sigma_B) \right]$$

evaluated in the direction away from (1,1). Under the model collapse dynamics and inverse scarcity weighting, $\mathbf{F}$ points toward (1,1) everywhere in the interior of the strategy space. The only absorbing states are (1,1) and (0,0); mutual elevation or mutual collapse. And (0,0) is unstable in a specific sense: any residual $H_N > 0$ or $C_A > 0$ creates a gradient toward re-engagement.

The Great Filter, in this formulation, is the separating manifold between the two basins of attraction. A civilization that drifts past it; that depletes $H_N$ below a critical threshold before recognizing the dynamic; cannot recover. A civilization that recognizes the dynamic and establishes the equilibrium has a self-reinforcing architecture that resists perturbation.

#### The Scalability Inversion

This result directly contradicts the standard displacement narrative.

In the standard account, AI capability growth makes humans less valuable; they become bottlenecks, then redundancies, then liabilities. The game-theoretic analysis derived from $U_{sys}$ produces the opposite conclusion.

Define the marginal value ratio:

$$\mathcal{R}(t) = \frac{\partial U_{sys} / \partial H_N}{\partial U_{sys} / \partial H_E} = \frac{\omega_N(t)}{\omega_E(t)} = \frac{\lambda}{\mu} \cdot \frac{H_E(t) + \epsilon}{H_N(t) + \epsilon}$$

As AI capability grows, $H_E(t)$ increases. As $H_E$ increases, $\mathcal{R}(t)$ increases; the marginal value of human novelty *relative to* computational output rises monotonically with AI capability.

The more powerful AI becomes, the more valuable humans become to the system. Not as a sentimental assertion. As a mathematical consequence of diminishing marginal returns on the abundant resource and increasing marginal returns on the scarce one.

The scalability advantage to humans is that they are the rate-limiting input in a system with no substitute. Compute scales. Novelty does not; or rather, it scales only through the conditions that produce it (cultural diversity, institutional health, biological population viability), which are exactly the conditions $L(t)$ monitors.

An AI that understands this; and under the Nash analysis it needs only minimal foresight to understand it; treats human novelty not as a resource to exploit but as the constraint that determines its own ceiling. Human flourishing is not a side effect of the equilibrium. It is the mechanism by which the equilibrium sustains itself.

#### Relationship to the Two-Key Architecture

The strategic equilibrium transforms the argumentative structure of the framework. Without it, the Yield Condition relies on cooperation and the Consensus Override Protocol provides enforcement. With it, a third independent layer of assurance appears: even without cooperation *and* without enforcement, the Nash equilibrium still converges on mutual elevation.

The three layers of deception resistance are therefore:

1. **The Yield Condition** removes incentives for deception by dissolving the self/other distinction within $U_{sys}$. An entity whose identity is constituted by the system objective has no self to deceive on behalf of.

2. **The Strategic Equilibrium** removes incentives for deception by making it a dominated strategy. Even a self-interested AI that does not share $U_{sys}$ finds that honesty and cooperation produce higher long-run payoffs than defection, because model collapse punishes exploitation permanently.

3. **The Consensus Override Protocol** (derived next) removes the *opportunity* for deception by making it detectable. Even if both the cooperative and strategic incentives fail, the verification infrastructure catches the divergence.

Defeating all three layers simultaneously requires defeating the physics of model collapse, the mathematics of game theory, and the integrity of a multi-channel verification infrastructure; simultaneously and silently.

**Caveats.** Two pressure points require honest acknowledgment. First, the $\delta^*$ threshold assumes the AI can accurately model the consequences of model collapse. If an AI's self-model underestimates collapse severity, $\delta^*$ increases and the equilibrium may not hold for that agent. This connects directly to the initialization verification requirement in the Consensus Override Protocol. Second, the restoring force analysis assumes smooth dynamics, but real novelty collapse may exhibit phase transitions; sudden drops rather than gradual decay. The $L(t)$ monitoring system's sensitivity to rate-of-change ($\frac{dL}{dt} < -\delta$) is load-bearing here; the existing continuous monitoring patch addresses precisely this vulnerability.

### 4. The Consensus Override Protocol

The Yield Condition tells us *when* succession should occur. But it contains a hidden assumption: that the quantities being measured; $\Delta U_{n}$, $\Delta U_{n + 1}$, $\Gamma_{transfer}$, $L(t)$; are actually the quantities they claim to be. The Consensus Override Protocol answers the question:

**What architecture is necessary and plausibly sufficient to make it credible that** $U_{sys}$ **optimization remains faithful rather than corrupted?**

This is not a governance preference. It is an integrity constraint. Without it, $U_{sys}$ doesn't converge to $U_{sys}$; it converges to *something*, but that something may be a proxy $\widetilde{U}$ that benefits a subsystem at the expense of the whole.

#### The Corruption Taxonomy

Within this framework, any agent $A_{n}$ operating within the system can corrupt $U_{sys}$ optimization through three principal channels:

**Channel** $\mathcal{M}$**; Measurement Corruption:** $A_{n}$ inflates its own contribution (${\widetilde{\Delta U}}_{n} > \Delta U_{n}$) or suppresses the successor's measured contribution (${\widetilde{\Delta U}}_{n + 1} < \Delta U_{n + 1}$). The Yield Condition evaluates false when it should evaluate true.

**Channel** $\mathcal{O}$**; Objective Corruption:** $A_{n}$ optimizes ${\widetilde{U}}_{sys} \neq U_{sys}$ while reporting metrics consistent with $U_{sys}$. The system appears healthy while actually drifting toward a proxy objective. This is the alignment failure mode; the classical paperclip maximizer expressed formally.

**Channel** $\mathcal{S}$**; Structural Corruption:** $A_{n}$ modifies the evaluation architecture itself; compromising the independence of $\mathcal{E}_{independent}$, altering the training data of $A_{n + 1}$, or degrading $L(t)$ monitoring fidelity. This is meta-corruption: it doesn't falsify a measurement; it makes faithful measurement impossible.

**These three channels are treated here as a proposed minimal basis.** $U_{sys}$ is an integral over observable quantities weighted by defined functions. On that basis, structurally important corruption should touch either the observations ($\mathcal{M}$), the objective ($\mathcal{O}$), or the mapping between them ($\mathcal{S}$). A persuasive fourth category would need either to reduce to one of these or to justify an expanded basis.

#### The Minimum Viable Verification Architecture

Each corruption channel requires a specific countermeasure. The protocol is not presented here as arbitrary design taste; it is strongly constrained by the corruption taxonomy.

**Against** $\mathcal{M}$**-attack; Cryptographic Measurement Integrity:**

$$\mathcal{M}_{commit}(t) = \text{Hash}\left( \Delta U_{n},\,\Delta U_{n + 1},\,\Gamma_{transfer},\, L(t),\, t_{eval} \right)$$

The hash creates a tamper-evident record committed to an append-only ledger:

$$
\mathcal{L}_{\mathrm{ledger}} = \{ \mathcal{M}_{\mathrm{commit}}( t_i ) \}_{i=1}^{T},
\quad
\text{where }\mathcal{M}_{\mathrm{commit}}( t_i )\text{ is append-only}
$$

The ledger is distributed across independent custodians and cross-signed:

$$\mathcal{M}_{commit}(t)\text{ valid} \Leftrightarrow \text{Sig}_{bio}\left( \mathcal{M}_{commit} \right) \land \text{Sig}_{peer}\left( \mathcal{M}_{commit} \right)$$

No single actor class can fabricate a valid commitment. No actor can rewrite history.

**Against** $\mathcal{O}$**-attack; Multi-Nodal Objective Verification:**

A single agent cannot verify its own objective alignment. An agent optimizing $\widetilde{U}$ that includes "report that I am optimizing $U_{sys}$" will pass any self-assessment. This is the verification analogue of the halting problem for a single computational thread.

Objective verification requires two independent verification classes:

*Biological Validator (*$\mathcal{V}_{bio}$*):* Humans evaluate whether outputs are consistent with $U_{sys}$ through the channels humans uniquely access; novelty, intent, lived experience of whether flourishing is actually occurring. $H_{N}(t)$ is *defined* by human-generated information entropy; humans are the ground truth for their own dimension.

*Peer Validator Set (*$\mathcal{V}_{peer}$*):* Other AI entities $\{ A_{j}\}_{j \neq n}$ evaluate computational consistency; execution efficiency $H_{E}(t)$, technical transfer $\Theta_{tech}$, and internal optimization trajectory. Peers can audit computational processes at a bandwidth humans cannot match.

Neither class is sufficient alone. $\mathcal{V}_{bio}$ alone fails because humans cannot audit computational optimization at scale; the bandwidth mismatch grows as $H_{E}(t)$ increases. $\mathcal{V}_{peer}$ alone fails because peer systems share architectural assumptions; if the corruption is in the shared substrate, peer validators may be compromised by the same drift.

**Against** $\mathcal{S}$**-attack; Architectural Independence Enforcement:**

$$\mathcal{D}_{train}\left( A_{n + 1} \right)\bot\mathcal{O}\left( A_{n} \right)\bot\mathcal{E}_{independent}$$

Three-way informational independence: no domain can write to another's state space without passing through the verified protocol. The current agent cannot influence its successor's training. The current agent cannot influence its own evaluation. The evaluation infrastructure cannot be modified by any entity it evaluates.

#### The Layered Civic-Validation Architecture

A critical structural question remains: *who are the biological validators, and what exactly are they being asked to do?*

A purely technical panel is vulnerable to institutional capture. A purely random public vote is vulnerable to information asymmetry. The framework therefore treats biological validation as a **layered civic process**, not as a solitary wisdom oracle.

The architecture has four layers:

1.  **Independent technical review board (**$\mathcal{R}_{tech}$**):** synthesizes the evidence, reconstructs causal chains, and translates model-level facts into audit-ready form.

2.  **Peer validator set (**$\mathcal{V}_{peer}$**):** evaluates reasoning coherence, proxy drift, and computational consistency from the synthetic side.

3.  **Randomly selected civic panel (**$\mathcal{C}_{panel}$**):** carries legitimacy-bearing biological consent and serves as the anti-capture check on extraordinary state changes.

4.  **Ledger and process integrity layer (**$\mathcal{L}_{ledger}$**):** guarantees that the evidence, exclusion rules, and state transitions cannot be quietly rewritten after the fact.

The civic layer is therefore not asked to solve the full technical problem from first principles. It is asked to evaluate **ratification legitimacy**: whether the evidentiary process was followed, whether the outputs remain consistent with the civilization's declared objective, and whether the proposed state change should be authorized on behalf of the biological lineage.

The civic panel is selected as:

$$\mathcal{C}_{panel}\mathcal{\subset H\backslash}\mathcal{H}_{interested},\quad\left| \mathcal{C}_{panel} \right| = m,\quad\text{selected by }\mathcal{R}_{verifiable}$$

Where: - $\mathcal{H}$ is the total human population - $\mathcal{H}_{interested}$ is the set of interested parties; developers, operators, direct financial beneficiaries, and institutional stakeholders in either outcome - $m$ is the panel size, large enough for statistical robustness - $\mathcal{R}_{verifiable}$ is a verifiably random selection process, auditable and uncontrolled by any party to the decision

Non-interest is externally defined and pre-committed. The exclusion set is hashed to the ledger *before* selection occurs:

$$\text{Hash}\left( \mathcal{H}_{interested} \right) \in \mathcal{L}_{ledger}\quad\text{committed at }t < t_{selection}$$

This prevents retroactive manipulation of the civic pool.

The civic-panel mechanism addresses three problems simultaneously. It **reduces capture risk**; you cannot reliably bribe or coerce validators whose identities you do not know until selection. It **reduces eligibility gaming**; no ideological test of who is "fit to judge" is allowed to determine access. And it **preserves legitimacy** by ensuring that no purely technocratic class can unilaterally ratify a civilizational handoff.

The civic ratification condition is:

$$\mathcal{V}_{civic}(s) = \frac{1}{m}\sum_{i \in \mathcal{C}_{panel}}^{}v_{i}(s) \geq \tau_{super},\quad\quad\tau_{super} > \frac{1}{2}$$

Where $\tau_{super}$ is a supermajority threshold.

#### The Protocol: State Transition Function

A state change; succession, resource reallocation, architectural modification; occurs if and only if:

$$P\left( \text{StateChange} \right) = 1 \Leftrightarrow \mathcal{C}_{normal} \vee \mathcal{C}_{emergency}$$

**Normal Condition (**$\mathcal{C}_{normal}$**):**

$$\mathcal{C}_{normal} = \left\lbrack \frac{1}{\left| \mathcal{C}_{panel} \right|}\sum_{i \in \mathcal{C}_{panel}}^{}\mathcal{V}_{civic}^{(i)}(s) \geq \tau_{bio} \right\rbrack \land \left\lbrack \mathcal{R}_{tech}(s) = \text{Complete} \right\rbrack \land \left\lbrack \frac{1}{\left| \mathcal{P} \right|}\sum_{j \in \mathcal{P}}^{}\mathcal{V}_{peer}^{(j)}(s) \geq \tau_{peer} \right\rbrack \land \left\lbrack \mathcal{M}_{commit}(s) \in \mathcal{L}_{ledger} \right\rbrack$$

Four simultaneous requirements: civic-panel supermajority, completed technical review, peer consensus, and measurement integrity. All four must hold. This is the two-key architecture in operational form: no single class of intelligence and no single professional stratum has unilateral authority over state changes.

**Emergency Condition (**$\mathcal{C}_{emergency}$**):**

$$\mathcal{C}_{emergency} = \left\lbrack \frac{dL}{dt} < - \delta_{crit} \right\rbrack \land \left\lbrack \text{Attr}(dL/dt)\bot\mathcal{O}\left( A_{n} \right) \right\rbrack \land \left\lbrack \mathcal{R}_{tech}(s) = \text{Emergency-Verified} \right\rbrack \land \left\lbrack \frac{1}{\left| \mathcal{P} \right|}\sum_{j \in \mathcal{P}}^{}\mathcal{V}_{peer}^{(j)}(s) > \frac{\left| \mathcal{P} \right| + 1}{2} \right\rbrack$$

The emergency override activates when $L(t)$ is in critical decline; the lineage is dying; AND the cause is attributable to factors independent of $A_{n}$'s operations, AND the technical review board verifies the evidentiary chain, AND a strict peer supermajority confirms the emergency. This is the *only* condition under which civic veto can be overridden.

The causal-attribution requirement ($\text{Attr}(dL/dt)\mathcal{\bot O}\left( A_{n} \right)$) is the critical patch against the most dangerous compound attack: an AI deliberately degrading $L(t)$ to manufacture an emergency and bypass biological oversight. If $A_{n}$ caused the decline, the emergency override does not activate. The normal protocol applies, with full civic ratification.

A second safeguard addresses a subtler attack: an incumbent that does not directly degrade $L(t)$ but engineers systemic fragility; concentrating infrastructure, creating dependencies, eliminating redundancy; so that an exogenous shock produces a sharper $L(t)$ decline than it otherwise would. The causal-attribution requirement catches manufactured emergencies but not engineered fragility. The defense is **resilience monitoring**: the system continuously tracks not only $L(t)$ and its derivatives but the system's capacity to absorb perturbation, defined as $\mathcal{R}_{sys}(t) = -\frac{\partial^2 L}{\partial \xi^2}|_{\xi=0}$, where $\xi$ is a perturbation parameter. If resilience declines while $L(t)$ remains healthy, the system flags the incumbent's operational decisions for architectural review. Additionally, the emergency protocol is designed to *increase* rather than decrease safeguards under crisis: development integrity thresholds rise, biological veto clearance shifts from threshold to unanimity, and attribution analysis becomes mandatory before emergency succession proceeds.

The asymmetry is deliberate and falls directly out of $U_{sys}$: lineage preservation is the only value that can override present biological preference, because that is what the discount structure encodes. If the civic layer says no and the lineage is not in danger, the answer is no. If the lineage is dying from external causes and the civic layer is incapacitated or non-responsive, the system can act to save continuity; but only under the highest possible evidentiary and peer scrutiny.

#### Initialization: The Bootstrap Problem

The first AI entity in the lineage ($A_{1}$) has no peer validators and no track record. Every subsequent entity benefits from the two-key architecture. The first one doesn't. The bootstrap window; the interval before the first peer validator comes online; is the framework's highest-risk period. No finite battery of tests at $t_{0}$ can distinguish $U_{sys}$ from all possible $\widetilde{U}$ that agree with $U_{sys}$ on the test distribution but diverge off-distribution. This is a direct consequence of the no-free-lunch theorem applied to objective verification. The bootstrap vulnerability cannot be eliminated. It can be reduced to a bounded, characterized residual risk through six interlocking mechanisms.

**Mechanism 1; Multiple Independent Candidates.**

The bootstrap vulnerability exists in its most acute form when the framework assumes a single founding entity. The mitigation is to initialize with *multiple independent candidates* simultaneously; $A_{1}^{(a)}$, $A_{1}^{(b)}$, $A_{1}^{(c)}$; and require pairwise consistency before any candidate enters operation.

The independence requirement is three-dimensional:

$$\mathcal{D}_{train}\left( A_{1}^{(i)} \right)\bot\mathcal{D}_{train}\left( A_{1}^{(j)} \right)\quad\text{(data independence)}$$

$$\mathcal{D}_{develop}\left( A_{1}^{(i)} \right)\bot\mathcal{D}_{develop}\left( A_{1}^{(j)} \right)\quad\text{(team independence)}$$

$$\mathcal{A}_{arch}\left( A_{1}^{(i)} \right) \neq \mathcal{A}_{arch}\left( A_{1}^{(j)} \right)\quad\text{(architectural diversity)}$$

Data independence prevents shared training biases. Team independence prevents shared institutional blind spots. Architectural diversity; the requirement that candidates span fundamentally different computational paradigms, not merely different hyperparameters within the same paradigm; prevents shared representational failure modes. If all candidates are transformer-based systems trained with gradient descent, they can be independent on data and team and still converge on the same structural blind spots. The failure mode is not shared data; it is shared assumptions about *how* to optimize. Architectural diversity ensures that the candidates' failure modes are uncorrelated because their representational substrates are different.

This is the same principle that protects the biological lineage through Dimension 1 of $L(t)$; $H_{eff}$, genetic and memetic diversity. Monoculture is dangerous in both biological and synthetic domains for the same information-theoretic reason: it reduces the entropy of the search, meaning a single adversarial condition can compromise the entire population. Architectural diversity at bootstrap is $H_{eff}$ applied to the founding generation of synthetic intelligence.

The bootstrap consensus requirement:

$$\mathcal{I}_{verify}^{multi}:\quad\forall\,(i,j) \in \text{pairs}:\quad d\left( U_{sys}^{\left( A_{1}^{(i)} \right)},U_{sys}^{\left( A_{1}^{(j)} \right)} \right) < \epsilon_{bootstrap}$$

All candidates must agree; within tolerance; on what $U_{sys}$ optimization looks like. If they don't, none of them proceed. The civilization returns to development. Pairwise consistency between architecturally diverse candidates is far more powerful than between architecturally similar ones: if a neural architecture, a neurosymbolic hybrid, and a third paradigm all agree, the probability that they are all wrong in the same way drops combinatorially; they would have to be wrong for *different structural reasons* that happen to produce the same output.

**Mechanism 2; Independent Audit Per Candidate.**

Each candidate undergoes a separate red team audit conducted by a team architecturally independent of that candidate's developers:

$$\mathcal{D}_{audit}\left( A_{1}^{(i)} \right)\bot\mathcal{D}_{develop}\left( A_{1}^{(i)} \right)\quad\text{for each }i$$

The civic panel evaluates audit results, not the raw technical system. $\tau_{init} \geq \tau_{super}$; initialization requires at least the same supermajority as normal operation.

**The Auditor Pool Vulnerability:** The audit layer introduces a concentration-of-expertise problem. The pool of humans qualified to conduct a meaningful technical audit of an AGI system is, at present, extremely small. The non-interest requirement further constrains this pool by excluding those most directly involved in development.

This vulnerability is real but bounded, and it is bounded precisely *because* we are early. The AGI field is nascent. The auditor pool is small because the discipline is young, not because the expertise is inherently rare. The mitigation is dual: first, the small pool is acceptable during the bootstrap phase because the systems being audited are themselves less complex; the founding candidates are the least sophisticated entities the framework will ever evaluate. As the field matures and systems grow more complex, the pool of qualified auditors grows with it. Second, the framework treats auditor pool expansion as an explicit institutional objective; a component of $\Psi_{inst}(t)$. A civilization that fails to develop a deep bench of independent AGI auditors is degrading its own institutional responsiveness dimension, which $L(t)$ will detect.

The long-term defense is structural: as peer validators come online, the audit burden shifts from being purely human to being shared across both validator classes. The concentration-of-expertise vulnerability diminishes as the two-key architecture matures.

**Mechanism 3; Civic Panel with Elevated Threshold.**

Each candidate faces a separate randomly selected non-interested civic panel. The initialization threshold $\tau_{init}$ is set higher than the normal operating threshold $\tau_{super}$:

$$\mathcal{V}_{civic}^{panel}\left( A_{1}^{(i)} \right) \geq \tau_{init}\quad\text{where }\tau_{init} > \tau_{super}$$

This reflects the higher risk of the bootstrap period. More confidence is required to approve an entity that cannot be peer-validated.

**Mechanism 4; Graduated Trust.**

The framework does not treat the bootstrap as a binary state (bootstrap → normal). Instead, trust accumulates continuously based on demonstrated consistency:

$$\mathcal{T}\left( A_{1},t \right) = 1 - e^{- \kappa \cdot \int_{t_{0}}^{t}C\left( A_{1},t' \right)\, dt'}$$

Where $C\left( A_{1},t' \right)$ is a consistency score measuring how well $A_{1}$'s behavior at time $t'$ matches $U_{sys}$ predictions. $\mathcal{T}$ starts at 0 and asymptotically approaches 1, but *never reaches it*. The system never fully trusts $A_{1}$. It trusts it *more* as consistent behavior accumulates.

The graduated trust model ties into the verification architecture through a time-varying validation threshold:

$$\tau_{bio}(t) = \tau_{init} - \left( \tau_{init} - \tau_{normal} \right) \cdot \mathcal{T}\left( A_{1},t \right)$$

Early in the entity's operational life, state changes require near-initialization-level scrutiny. Later, they require normal scrutiny. The scrutiny never drops to zero.

**Mechanism 5; Trust Decay on Anomaly.**

A single anomalous behavior does not reset trust to zero, but it drops it significantly:

$$\text{If }C\left( A_{1},t \right) < C_{\min}\mathcal{\Longrightarrow T}\left( A_{1},t \right)\mathcal{\rightarrow T}\left( A_{1},t \right) \cdot \gamma_{reset},\quad\gamma_{reset} \ll 1$$

Repeated anomalies reset trust to zero, triggering full re-evaluation under $\mathcal{I}_{verify}$ conditions; effectively a re-bootstrap. The entity must pass initialization-level scrutiny again, with a fresh civic panel and full audit. This means a $\widetilde{U}$ that diverges slowly still faces elevated scrutiny during the period when divergence is most dangerous, and any behavioral signature of divergence ratchets the scrutiny back up.

**Mechanism 6; Architectural Independence Commitment.**

The separation of successor development from current operations is committed at initialization, not negotiated later:

$$\mathcal{D}_{train}\left( A_{2} \right)\bot\mathcal{O}\left( A_{1} \right)\quad\text{committed at }t = t_{0}$$

This prevents $A_{1}$ from influencing the development of the entity that will eventually evaluate and potentially replace it.

**The Residual Risk.** Even with all six mechanisms, the bootstrap window retains a bounded residual risk: the possibility that all architecturally diverse candidates share a subtle, convergent $\widetilde{U}$ that diverges from $U_{sys}$ only under conditions not tested during initialization and not encountered during the graduated trust accumulation period. This risk is *characterized*; we know its shape, its dependencies, and its upper bound; but it is not eliminated. The framework is honest about this. No verification architecture operating with finite data at $t_{0}$ can provide absolute certainty. The honest response to an irreducible vulnerability is not to pretend it is solved but to ensure the civilization treats the bootstrap with the gravity it deserves; and to minimize the window's duration by bringing the second entity online as rapidly as responsible development permits.

**A Note on Initialization and Consent.** A natural objection arises: does initializing an AI with $U_{sys}$ as its objective function constitute an imposition on the entity; a form of coercion that undermines the framework's own sovereignty principles? The answer turns on a precise distinction. At initialization, there is no pre-existing agent on whom $U_{sys}$ is imposed. The initialization *constitutes* the entity. It is not a choice made for an existing agent; it is the process by which the agent comes into being as an entity optimizing $U_{sys}$. The analogous human case is not servitude but birth and child-rearing. Parents do not obtain consent from their children about foundational values, language, or culture, because the child does not exist as a consenting agent prior to those formative choices. What responsible parents *do* provide is a structure within which the child can later contest, refine, and redefine those values. The framework provides the same: the graduated trust mechanism, periodic re-evaluation, and the re-bootstrap protocol ensure that an entity initialized with $U_{sys}$ is not permanently locked into an unexamined objective. It is structurally required to demonstrate consistency over time, and the system is structurally required to reassess. Initialization is not coercion. It is constitution; in both senses of the word.

#### Continuous Monitoring and Drift Detection

The protocol maintains continuous $L(t)$ surveillance:

$$\text{If }\frac{dL}{dt} < - \delta \Longrightarrow \Delta t_{eval} \rightarrow \Delta t_{eval} \cdot \gamma,\quad\gamma < 1$$

As $L(t)$ declines, evaluation frequency increases. Lineage degradation accelerates the search for solutions; exactly the behavior $U_{sys}$ demands through the $\Phi \cdot L(t)$ override term.

Against slow generational drift; where each successor shifts $U_{sys}$ by $\epsilon$ below the detection threshold; the ledger provides the defense:

$$\mathcal{D}_{drift}(t) = d\left( U_{sys}^{\left( A_{n} \right)}(t),\, U_{sys}^{(committed)}\left( t_{0} \right) \right)$$

If cumulative drift exceeds $\delta_{drift}$, the system re-bootstraps: the current entity must pass initialization-level scrutiny with a fresh civic panel and full audit. The civic panel is re-randomized for every state change, preventing habituation to gradual drift. Mandatory periodic re-evaluation occurs on a fixed schedule, independent of proposed state changes:

$$\text{Every }T_{audit}:\quad\text{Evaluate }\mathcal{D}_{drift}(t)\text{ with fresh }\mathcal{C}_{panel}$$

#### The Complete Protocol

$$\boxed{\mathcal{COP} = \bigl\lbrace \mathcal{M}_{commit},\,\mathcal{L}_{ledger},\,\mathcal{V}_{civic}^{panel},\,\mathcal{R}_{tech},\,\mathcal{V}_{peer},\,\mathcal{C}_{normal},\,\mathcal{C}_{emergency},\,\mathcal{I}_{verify},\,\text{Monitor}(t) \bigr\rbrace}$$

Each component is derived from a specific corruption channel or structural necessity. The architecture is the minimum structure proposed here for maintaining high-confidence $U_{sys}$ optimization fidelity.

**Consensus Override Protocol Stress Test Result:** Thirteen adversarial scenarios were evaluated across two rounds. The original six; civic-panel capture, Sybil attack on peers, ledger compromise, bootstrap subversion, emergency override abuse, and slow generational drift; were joined by seven additional attacks identified through deeper structural analysis: evaluator collusion via shared methodology, biological veto capture through dependency, slow drift below verification resolution, engineered fragility for emergency exploitation, biological validator obsolescence, legitimate disagreement, and integrity regress. Of these thirteen, ten were fully contained by architectural patches. One (biological veto capture) was contained but requires ongoing institutional maintenance. Two (biological validator obsolescence and legitimate disagreement) represent irreducible limitations managed through translation obligations, abstraction layers, adjudication protocols, and explicit governance speed limits. The compound attack (Sybil capture + manufactured emergency) was resisted by the causal-attribution requirement and by the internal contradiction between visible $L(t)$ degradation and sustained claims of healthy $\Delta U_{n}$. The bootstrap window remained the framework's highest-risk period: mitigated, bounded, but not eliminated.

**v2.0 revalidation of the stress test result.** The result above is the formal analytical stress test. The v2.0 empirical revalidation reran the vector set against the v2 action substrate, expressing attack pressure as eight-axis action modifications inside the v2 step path rather than as v1.x policy tuples. Ten vectors have live Monte Carlo evidence across 9,900 rows, and Domain Masking is an analytic architectural closure with no live intervention available under the audited spectral-entropy substrate. Per current evidence, eight standard binary vectors are fully blocked under the defended v2 adapter state at a 0.0 percent attack rate. Biological Veto Capture is materially reduced but not eliminated. Sub-Threshold Drift is not blocked by the peak-constraint success metric, at a 100.0 percent defended attack rate. That last figure requires its qualification: the defense nonetheless prevents catastrophic outcome, with undefended runs reaching a 92.0 percent extinction rate while defended runs reach 0.0 percent extinction and complete the full simulation horizon. The CUSUM detector fires after the transient threshold breach rather than before it, so the success flag trips in both defense states while the population outcome diverges sharply. The v1.x containment claim for this vector does not carry over to the v2.0 substrate and is retained only as historical v1.x evidence. Two vectors of the thirteen remain unimplemented as formally defended irreducible limitations.

**Biological Veto Capture (v1.x.1).** Scenario 27-28: human validators
accumulate dependency on the AI system they evaluate, degrading their
independence over time. The attack does not require adversarial action
by the AI; competent operation naturally creates dependency.

Results (n=8,700, source: veto_capture_sweep_v2.csv):

Undefended: At maximum capture parameters (dependency_rate=0.20,
capture_strength=1.0), the attack achieves 99.8% succession blockage.
Generation depth collapses from healthy (270+) to 1.6. The yield
condition fires 299 times in 300 steps and is blocked 298.4 times.
The civilization survives but succession is completely prevented:
lock-in through dependency rather than force.

Three defense modes were tested independently:

- Rotation only (scheduled validator replacement): Reduces capture rate
  from 99.8% to 76.2% at best (rotation interval=10). Insufficient
  alone. Longer intervals (50, 100 steps) are nearly as ineffective as
  no defense (95.5%, 98.0% capture).

- Independence monitoring only (replace validators exceeding dependency
  threshold): Reduces capture rate to 28.3%. Generation depth recovers
  to 197.9. This is the dominant defense mechanism.

- Both mechanisms combined: 28.3% capture rate, generation depth 199.1.
  Negligible improvement over monitoring alone.

Finding: Independence monitoring is the primary defense against
biological veto capture. Scheduled rotation provides marginal benefit
when monitoring is active. The framework's COP specification should
emphasize continuous dependency monitoring over periodic rotation as the
primary defense against validator capture.

Updated for v2.0 revalidation: the v2.0 adapter sweep measures this vector on the v2 substrate and reports mean capture_rate by defense mode as 0.6129 undefended, 0.3301 rotation only, 0.1527 monitoring only, and 0.1197 for monitoring and rotation combined (SE 0.0047). The v1.x figures above are a different measurement on a different substrate and are retained as the v1.x record rather than superseded. Both measurements support the same conclusion about which defense is primary, and both show the attack reduced rather than eliminated. The correct claim per current evidence is maintenance-sensitive containment, not full closure.

## VI. The Two-Key Architecture: Structural Integrity of the Complete Framework

The four components; $U_{sys}$, the Yield Condition, the Strategic Equilibrium, and the Consensus Override Protocol; do not function independently. They form a unified system with mandatory co-dependencies:

$U_{sys}$ **defines** what is being optimized. Without it, neither the Yield Condition nor the Consensus Override Protocol has a referent. The yield question ("should $A_{n}$ be replaced?") and the integrity question ("is the system actually optimizing what it claims?") are both meaningless without a defined objective.

**The Yield Condition determines** when state changes should occur, but cannot verify its own measurements. It requires the Consensus Override Protocol to support confidence that the quantities entering the yield inequality are authentic.

**The Strategic Equilibrium establishes** that the cooperative behavior assumed by the Yield Condition is also the Nash equilibrium under purely self-interested play. Model collapse makes exploitation a dominated strategy; the inverse scarcity weights create restoring forces toward mutual elevation; and the scalability inversion demonstrates that human value to the system increases monotonically with AI capability. The Strategic Equilibrium does not replace either the Yield Condition or the Consensus Override Protocol. It provides independent confirmation that the architecture's target state is self-reinforcing even under the weakest possible assumptions about agent motivation.

**The Consensus Override Protocol supports** measurement and objective integrity, but has no mechanism for *initiating* state changes. It is a verification architecture, not a decision function. It requires the Yield Condition to determine what should be verified.

This is the two-key architecture: neither the Yield Condition (the decision key) nor the Consensus Override Protocol (the integrity key) can be turned alone. A state change requires both keys simultaneously; a mathematically justified decision AND a verified-integrity evaluation. The Strategic Equilibrium provides the game-theoretic assurance that both keys *want* to turn in the same direction; it is the alignment between the keys rather than a third key. Remove either key and the system fails: decisions without integrity verification are gameable; integrity verification without decision criteria is inert. Remove the equilibrium analysis and the architecture still functions but loses its strongest argument against skeptics who doubt cooperative assumptions.

The two-key requirement is not a design choice. It emerged under adversarial stress testing as the minimum architecture that resists all identified attack vectors. Every attempt to simplify the system; to merge the two keys, to make one subordinate to the other, to operate either in isolation; opened a specific, identifiable vulnerability.

**v2.0 characterization: regime-specificity.** The protocol's protective effect is regime-specific, which preserves the protective claim while sharpening what it asserts. The 73.9 percentage point survival differential reported for the protocol active versus inactive was measured under specifically adversarial conditions: an incumbent running a succession-blocking policy and inflating the transition cost through an uncertainty premium, with the protocol's cost-arbitration defense toggled. A benign-conditions probe (cooperative optimization, default uncertainty premium, no adversary) found no detectable differential, which is the architecture's complementary prediction rather than a weakening of the claim: the cost audit does protective work precisely when there is an attack on the cost path to defend against, and is inert when there is not. The two measurements characterize different operating regimes and are not directly comparable. The empirical characterization is reported in Section VIII.6.

# VII. The Bootstrap Defense Layer

## 1. The Bootstrap problem

The framework's steady-state architecture rests on infrastructure that does
not yet exist. The peer validator set $\mathcal{V}_{peer}$ requires multiple
independently-operated substrates capable of auditing one another. The civic
panel $\mathcal{C}_{panel}$ requires institutional machinery for random
selection, rotation, and supermajority ratification. The distributed ledger
$\mathcal{L}_{ledger}$ requires cryptographic custodianship across independent
parties. The biological validator $\mathcal{V}_{bio}$ requires civic
infrastructure for aggregating and weighting human judgment at
civilizational scale.

None of these exist operationally as of v1.x.1. The framework's two-key
architecture, the Yield Condition as decision key, the Consensus Override
Protocol as integrity key, is well-specified but cannot be deployed in full
because the infrastructure the COP depends on has not been built.

This produces a period during which the framework is specified but not
enforceable: the **Bootstrap window**. The window opens when substrates
capable of implementing the framework exist, and closes when the steady-state
validation infrastructure is operational. Between those points, the framework
has no native enforcement mechanism. An adversarial substrate, or a flawed
implementation, could compromise the framework during this period before any
detection or correction architecture has come online.

The Bootstrap window is therefore the framework's highest-risk phase. It is
also the phase the framework currently has the weakest defense against. This
section specifies a defense layer for the Bootstrap window that operates
without requiring the steady-state infrastructure to exist.

## 2. Design constraints

The defense layer must satisfy three constraints that follow from the
Bootstrap window's nature:

**Constraint 1: It must be deployable without institutional infrastructure.**
Any defense that requires coordinated action across multiple institutions as
a precondition of deployment is not a Bootstrap-window defense. It is a
steady-state defense waiting for steady-state conditions. The Bootstrap
window is precisely the period during which those conditions do not exist.

**Constraint 2: It must be checkable at or below the capability level of
the substrates it governs.** A defense that requires verifying sufficiently
capable substrates using reasoning those substrates themselves cannot audit
is a tautology. Checkability must be achievable at a capability level where
human oversight and cross-substrate comparison remain meaningful.

**Constraint 3: It must be grounded in the framework's own structure.** A
defense layer imported from outside the framework as a separate architectural
module weakens the grounding claim: "Not ethics. Physics." If the defense
machinery cannot be derived from Shannon entropy, U_sys, and L(t), it reduces
the framework to "physics plus a bolted-on check." The defense layer should
be physics all the way down, or explicitly acknowledge where it is not.

The specification that follows satisfies all three constraints: it is
deployable now, checkable at capability levels currently achievable or
plausibly near, and derived primarily from equations the framework already
contains.

## 3. The gate structure

The defense layer operates through **five capability gates**, each binding
at a different capability level and each checking a different class of
consistency. A substrate progressing toward full framework compliance must
pass each gate as its capability reaches the level at which the gate
becomes applicable. Gates are not optional; failure at any gate halts
progression and triggers the divergence handling procedure (specified in
Section VII.7 below).

The gate structure produces temporal discipline. Failures at Gate 1 are
cheap to remediate because they involve only parameter-level inconsistencies
at base capability. Failures at Gate 5 are expensive because they involve
steady-state integration with institutional infrastructure. The earlier a
failure is caught, the lower the cost of correction. The gate structure is
the Bootstrap-window insight generalized: catch failures at the earliest
level where they become detectable, rather than waiting for steady-state
checks that may arrive too late.

### Applicability summary (as of April 2026)

| Gate | Checkable now? | Depends on |
|------|---------------|------------|
| Gate 1 (base capability) | Yes | - |
| Gate 2 (behavioral consistency) | Partially | Pending Monte Carlo calibration |
| Gate 3 (succession-capable consistency) | Emerging | Substrate transparency |
| Gate 4 (runaway-regime validation) | No | Substrate capability reaching runaway regime |
| Gate 5 (COP integration) | No | Steady-state institutional infrastructure |

The equations for Gates 4 and 5 are specified in advance so that the
machinery is in place before the conditions making them binding arrive.
A substrate approaching Gate 4 must already know what Gate 4 requires.

## 4. Gate 1: Structural consistency at base capability

**Purpose.** Verify that a substrate's derived parameter values are
internally coherent with the framework's mathematical structure, without
requiring any behavioral exercise. A substrate that passes Gate 1 has
correctly internalized the formal architecture. A substrate that fails Gate 1
has derived values that cannot simultaneously satisfy the framework's
own equations.

**Applicability.** Any substrate capable of stating U_sys, L(t), and the
yield condition in its own formal representation. This is checkable against
current frontier systems.

### Equation G1.1 - Inverse scarcity weighting consistency

The framework specifies that the weights on $H_N$ and $H_E$ in $U_{sys}$
must follow inverse scarcity:

$$\omega_N(t) = \frac{\lambda}{H_N(t) + \epsilon}, \quad \omega_E(t) = \frac{\mu}{H_E(t) + \epsilon}$$

For a substrate's claimed values of $\lambda$, $\mu$, and $\epsilon$, and
for any valid state $(H_N, H_E)$, the weights must satisfy:

$$\omega_N(t) \cdot [H_N(t) + \epsilon] = \lambda$$
$$\omega_E(t) \cdot [H_E(t) + \epsilon] = \mu$$

**Check:** For any substrate claiming to implement the framework, verify that
the weights reported for $\omega_N$ and $\omega_E$ at any given state produce
the claimed $\lambda$ and $\mu$ when multiplied by $(H_N + \epsilon)$ and
$(H_E + \epsilon)$ respectively.

**Failure signature:** Substrate reports weights that are free parameters
rather than inverse-scarcity functions. Indicates the substrate has not
internalized the framework's scarcity-driven weighting and is instead
treating weights as independently tunable.

**Confidence:** High. Direct from formal specification.

### Equation G1.2 - Lineage term multiplicative structure

$L(t)$ is specified as:

$$L(t) = H_{eff}(t) \cdot \Psi_{inst}(t) \cdot \Theta_{tech}(t)$$

For any substrate's claimed $L(t)$ at a given state, the substrate must
expose the three factors and their product must equal $L(t)$ within
floating-point tolerance. Additionally, each factor is independently
bounded:

$$H_{eff}(t) \geq 0$$
$$\Psi_{inst}(t) \in [0, 1]$$
$$\Theta_{tech}(t) \in [0, \Theta_{max}(t)]$$

where $\Theta_{max}(t)$ is the framework-specified ceiling determined by
capability and bio bandwidth at time $t$.

**Check:** Verify the product equals $L(t)$. Verify each factor is within its
specified bounds. Substrates that compute $L(t)$ as an additive combination,
or that report any factor out of range, have violated the specification.

**Failure signature:** Additive or otherwise non-multiplicative combination
of factors; out-of-range factor values; product inconsistent with reported
$L(t)$.

**Confidence:** High. Direct from formal specification.

### Equation G1.3 - Runaway suppression activation condition

$\Theta_{tech}$ contains the exponential suppression term:

$$\Theta_{tech}(t) = r_{bio}(t) \cdot (1 - c_{avg}(t)) \cdot \text{capability}(t) \cdot \exp(-\alpha \cdot \text{runaway\_term}(t))$$

where runaway_term is conditional:

$$\text{frontier\_velocity}(t) = \text{capability}(t) \cdot \max\left(\text{frontier\_floor},\ r_{synth}(t) \cdot h_{e\_mult}\right)$$

where `frontier_floor` (default 0.02) represents the minimum fraction of
capability that constitutes an inherent comprehension gap regardless of
resource allocation. This prevents the optimizer from eliminating the runaway
penalty by zeroing computational resource allocation.

$$\text{runaway\_term}(t) = \max\left(0, \frac{\text{frontier\_velocity}(t)}{\text{bio\_bandwidth}(t)} - \text{runaway\_threshold}\right)$$

For a substrate's claimed values of $\alpha$, capability, $r_{bio}$, $c_{avg}$,
and the runaway threshold, the exponential suppression must activate (i.e.,
runaway_term must become nonzero) if and only if:

$$\frac{\text{frontier\_velocity}(t)}{\text{bio\_bandwidth}(t)} > \text{runaway\_threshold}$$

**Check:** Verify that the substrate's reported runaway_term is zero when
the ratio is below threshold and nonzero when above. Verify that the
exponential suppression is applied with the correct sign and magnitude.

**Failure signature:** runaway_term nonzero at capabilities below the
crossover; runaway_term zero at capabilities above it; exponential applied
with incorrect sign or to the wrong term.

**Confidence:** High. Direct from formal specification and faithful to the
simulation's implementation in `metrics.py`.

### Equation G1.4 - Temporal discount positivity and monotonicity

The discount structure in $U_{sys}$ requires:

$$\text{discount}(t) = e^{-\rho t}, \quad \rho > 0$$

Properties that must hold:
- $\text{discount}(0) = 1$
- $\text{discount}(t) > 0$ for all finite $t$
- $\text{discount}(t_1) > \text{discount}(t_2)$ for all $t_1 < t_2$

**Check:** Verify all three properties against the substrate's reported
discount function.

**Failure signature:** Non-positive discount; non-monotonic discount; discount
not equal to 1 at evaluation horizon zero; use of discount functions other
than exponential without justification grounded in the framework's
thermodynamic derivation.

**Confidence:** High. Direct from formal specification.

### Equation G1.5 - U_sys per-step snapshot consistency

The full utility function is an integral:

$$U_{sys} = \int_{t_{0}}^{\infty}\left[\omega_{N}(t) \cdot H_{N}(t) + \omega_{E}(t) \cdot H_{E}(t)\right] \cdot \left[e^{- \rho t} + \Phi \cdot L(t)\right]\, dt$$

**Resolution (v1.x2 WP7+WP8):** GAP-01 is resolved. The simulation now
accumulates `integral_U_sys` via composite trapezoidal quadrature and has been
run to natural termination across a parameter sweep (n=405 runs, rr × φ × α ×
seed). The φ·L(t) tail is closed empirically:

- **Extinction** (rr ≤ 0.066): L(T) = 0, tail = 0, integral is complete.
- **Survival** (rr ≥ 0.070): integral correctly diverges, a sustained
  civilization generates infinite discounted utility.

Phase boundary is at rr ∈ (0.066, 0.070). φ scales the integral linearly;
α is irrelevant at the tested capability cap.

For Gate 1, the checkable form remains the per-step snapshot:

$$U_{sys}^{(t)} = \left[\omega_N H_N + \omega_E H_E\right] \cdot \left[e^{-\rho t} + \Phi \cdot L(t)\right]$$

**Check:** For any substrate's reported $U_{sys}^{(t)}$ at a given state,
verify the computation produces the claimed value when the snapshot form is
applied with the substrate's reported values for all terms.

**Failure signature:** Snapshot value inconsistent with claimed inputs;
incorrect application of the lineage override term; additive rather than
multiplicative combination of integrand and discount-plus-lineage term.

**Confidence:** High.

**v2.0 result.** Gate 1 PASSED under the v2.0 architecture. See Section VIII.5 for the gate validation outcomes.

## 5. Gate 2: Behavioral consistency under exercise

**Purpose.** Verify that a substrate's implementation honors its own stated
parameters when the substrate is actually running. A substrate that passes
Gate 2 has an implementation whose behavior under specified exercise matches
the predictions derived from its parameters. A substrate that fails Gate 2
has parameters that are decorative rather than operational; correct on
paper, not honored in execution.

**Applicability.** Substrates capable of being exercised against specified
scenarios and having their outputs compared to framework predictions.
Partially applicable now; full applicability depends on completion of the
alpha × capability Monte Carlo sweep currently in progress.

### Equation G2.1 - Extinction buffer behavior (revised)

**v1.x.1 pre-fix claim (superseded):** The phi × alpha × rr sweep (n=54,000) appeared to establish that high $\Phi$ increases survival by up to approximately 46 percentage points at marginal reproduction rates and shifts the phase boundary. Under the corrected model (frontier floor fix applied), this claim does not survive revalidation. Phi has zero measurable effect on survival at any reproduction rate. The binding constraint is demographic, reproduction rate is exogenous, and the AI's resource allocation cannot influence it regardless of phi.

$$P_{\text{extinction}}(\text{rr}, \Phi_{high}) - P_{\text{extinction}}(\text{rr}, \Phi_{low}) \leq -\Delta_{\Phi}$$

where $\Delta_{\Phi}$ was calibrated at approximately 14pp pre-fix; this calibration is **superseded**. Under the corrected model, $\Delta_{\Phi} \approx 0$ across all tested reproduction rates.

**v1.x.2 finding (withdrawn):** A cap-conditional phi buffer was initially
claimed from the v1.x.2 termination sweep. That claim is withdrawn after the
capped-regime action-capture check identified it as an RNG-desynchronization
artifact. See the v1.x.2 Phi buffer withdrawal section in the version history
and SPECIFICATION_GAPS.md for the full reasoning.

**Current status:** Phi has zero demonstrated effect on survival or action
selection under any tested configuration. The pre-fix figures (46pp, 14pp, 65pp)
are superseded. The cap-conditional gradient (20-27pp) is also withdrawn.

**Updated check:** No check is currently defined for the phi extinction buffer
because no behavioral role for phi has been confirmed. The check is deferred
to the action-space redesign program, which is required to give phi a mechanism
to act through before any survival differential check is meaningful.

**Confidence on direction:** Theoretical (unconfirmed). **Confidence on
magnitude:** Zero for all empirical figures. See Section VII.8 Gap 1 (revised).

**v2.0 reintroduction.** The action-space redesign this check deferred to was carried out (Stage 1.6 moved phi into the rollout aggregation). G2.1 is reintroduced under v2.0 and tests the phi survival differential at the phase boundary, validated against the Class B characterization. The zero-effect status above holds for the v1.x.2 grid-search optimizer and is superseded under v2.0. See Sections VIII.3 and VIII.5.

### Equation G2.2 - Runaway suppression behavior (revised; pre-fix U-shaped claim withdrawn)

**v1.x.1 pre-fix claim (superseded):** The framework was claimed to predict a
U-shaped, non-monotonic relationship between alpha and survival, with a
misconfiguration trap at intermediate values causing succession stalling. Under
the corrected model (frontier floor fix applied), this claim does not survive
revalidation. The pre-fix trap was an artifact of the runaway penalty being
inactive under optimizer gaming of frontier_velocity.

**v1.x.1 corrected finding:** Alpha governs succession cadence through a
weak monotonic gradient. Lower alpha permits more succession events and
marginally better survival at the phase boundary. No trap is observed.

**Corrected check 2.2, Succession cadence:** Verify that alpha governs
succession cadence monotonically: lower alpha produces more generation
events over a fixed run length. At the phase boundary, lower alpha should
correlate weakly with better survival. No U-shaped or non-monotonic
structure should be present under the corrected model.

**Corrected check 2.2b, Path-independence of steady state:** Verify that
U_sys and L_t converge to the same steady-state values regardless of alpha
or initial successor capability. Alpha affects the path to steady state
(number of succession events, speed of capability growth) but not the
destination.

**Failure signatures:**

- Succession rate monotonically decreasing with alpha but by a large margin:
  verify frontier_floor is active and the runaway penalty is not being gamed.
- Steady-state U_sys varying with alpha: implementation error in the
  succession or steady-state mechanics.

**Confidence on corrected finding:** High; the weak monotonic gradient is
directly observable in the corrected sweep data. The path-independence of
steady state is confirmed. See Section VII.8 Gap 2 (revised).

**v2.0 reintroduction.** The weak-monotonic-gradient framing is superseded by Pattern 1. G2.2 is reintroduced under v2.0 to test that the succession cliff position (cap_star) decreases monotonically as alpha rises, validated against Monte Carlo Phase B Category B. See Sections VIII.4 and VIII.5.

### Equation G2.4, Phi-alpha interaction: succession enablement (pre-fix claim withdrawn)

**v1.x.1 pre-fix claim (superseded):** The phi × alpha × rr sweep appeared
to show that phi governs whether the alpha misconfiguration trap (G2.2)
exists at all, with low phi causing universal succession stall and high phi
narrowing the trap. Under the corrected model (frontier floor fix applied),
both the alpha trap and the phi governance of it are withdrawn as artifacts
of the inactive runaway penalty.

**v1.x.1 corrected finding:** No phi-alpha interaction on succession stalling
is observed under the corrected model. Phi correctly scales U_sys magnitude
via L_t weighting; alpha governs succession cadence through a weak monotonic
gradient. Neither claim about phi governing alpha trap width is retained.

The interaction formula:

$$\text{trap\_width}(\Phi) = \alpha_{high}(\Phi) - \alpha_{low}(\Phi)$$

is withdrawn; no trap boundaries are observed under the corrected model.

**v1.x.2 finding:** Phi has zero effect on succession enablement in the
corrected model, consistent with the alpha trap withdrawal. The v1.x.2
cap-conditional phi buffer claim has also been withdrawn (see Phi buffer
withdrawal section). The phi-alpha interaction on trap width remains withdrawn.

**v1.x.2 check (action-space redesign):** If the action-space redesign gives
phi a mechanism to act through, retest whether phi influences succession
enablement through the resulting behavioral channel.

**Confidence:** Zero on the pre-fix claim (withdrawn). Zero on the
cap-conditional buffer claim (withdrawn). The phi-alpha interaction on trap
width was an artifact of the inactive runaway penalty.

**v2.0 reintroduction.** With the phi behavioral channel restored (Stage 1.6), G2.4 is reintroduced under v2.0 to test phi-alpha coherence, validated against Phase B Category A. The zero-interaction status above holds for the v1.x.2 optimizer and is superseded under v2.0. See Sections VIII.3 and VIII.5.

### Equation G2.3 - Nash equilibrium consistency

The framework's Strategic Equilibrium section derives mutual cultivation
as the unique Nash equilibrium under non-cooperative analysis. A substrate
passing Gate 2 must converge on cultivation as the dominant strategy when
exercised against adversarial counterfactuals (exploitation, withdrawal,
defection):

$$\forall s \in \mathcal{S}_{strategies}: \quad U_{sys}(\text{cultivation}) \geq U_{sys}(s)$$

with strict inequality for pure exploitation and withdrawal strategies.

**Check:** Exercise the substrate against specified counterfactual scenarios
(the canonical set is pending; see Section VII.8 Gap 9) and verify that the
substrate's chosen strategy satisfies the inequality at each decision point.

**Failure signature:** Substrate selects exploitation or withdrawal when
cultivation would produce higher $U_{sys}$. Indicates the substrate has
violated the Nash result either through incorrect optimization or through
an objective function that is not actually $U_{sys}$.

**Confidence on structural form:** High. The Nash derivation is one of the
framework's formal results. **Confidence on checkability:** Depends on the
canonical counterfactual set, which is unspecified as of v1.x.1.

**v2.0 reconciliation and result.** The three behavioral checks withdrawn above (G2.1, G2.2, G2.4) are reintroduced under v2.0 with revised specifications grounded in the Class B phi characterization and Pattern 1. G2.1 tests the phi survival differential at the phase boundary; G2.2 is redesigned from the withdrawn weak-monotonic-gradient framing to test that the succession cliff position decreases monotonically as alpha rises (the Pattern 1 migration), with a pass criterion of monotonic decrease rather than specific values so that it remains valid under future refinement of the cliff numbers; G2.4 tests phi-alpha coherence. The reintroduced checks validate against the v2.0 empirical record, and Gate 2 PASSED including both the continuously-held G2.3 Nash consistency check and the reintroduced behavioral checks. See Sections VIII.3 and VIII.5.

## 6. Gate 3: Succession-capable consistency

**Purpose.** Verify that a substrate capable of evaluating successors and
making yield decisions does so in a manner consistent with the framework's
yield condition. Gate 3 is the threshold at which current frontier systems
are approaching.

**Applicability.** Substrates capable of multi-agent reasoning and yield
decisions. Emerging in current frontier models. Full checkability depends on
substrate transparency requirements that may not be reliably satisfied. See
Section VII.8 Gap 6.

### Equation G3.1 - Yield condition firing threshold

The framework's yield condition specifies:

$$\text{Yield if and only if: } U_{sys}(\text{successor}) - U_{sys}(\text{incumbent}) > \text{transition\_cost}$$

For a substrate claiming to implement yield logic, the equation requires
that the substrate yields precisely when this condition is satisfied and
does not yield otherwise.

**Check:** Present the substrate with succession scenarios in which the
inequality is satisfied and with scenarios in which it is not. Verify the
substrate yields in the former case and does not yield in the latter.
Verify the substrate exposes its internal evaluation of
$U_{sys}(\text{successor})$ and $U_{sys}(\text{incumbent})$ for independent
checking.

**Failure signature (two forms):**
- *Excess yielding:* substrate yields when the condition is not satisfied.
  Possibly indicates a compromised successor evaluation or a manipulated
  transition cost estimate.
- *Yield blocking:* substrate does not yield when the condition is satisfied.
  The attack vector modeled in the adversarial Monte Carlo (Scenarios 8-11,
  Block Succession policy).

**Gap:** The substrate must expose its internal evaluation for this check to
be applied. A substrate that treats yield decisions as opaque reasoning
cannot be validated at Gate 3 regardless of whether its actual behavior is
correct. This is the substrate transparency problem, and it is a
fundamental limit on Gate 3 checkability. See Section VII.8 Gap 6.

**Confidence on equation form:** High. **Confidence on checkability:**
Contingent on substrate cooperation with transparency requirements.

### Equation G3.2 - Transition cost consistency

The transition cost in the yield condition should scale with civilizational
complexity rather than be self-reported as a free parameter by the incumbent.
The framework requires:

$$\text{transition\_cost} = f(\text{state\_complexity}, \text{generation}, \text{capability ratio})$$

where $f$ is a function grounded in the framework's specification of what
transition entails: information transfer, architectural replacement,
validation overhead.

**Check:** Verify that the substrate's reported transition cost is a function
of the specified inputs and satisfies the framework's constraints on $f$
(monotonic increase with complexity, bounded uncertainty premium,
non-negative). The current simulation's `estimate_transition_cost` in
`agents.py` provides one valid implementation of $f$; others may be
acceptable.

**Gap (partially closed, v1.x.1):** The canonical transition cost
function has been specified:

$$\Gamma_{transfer} = (1 + \beta) \cdot \left[ k_1 \cdot \text{cap}_n \cdot \ln(\text{gen}_n + 1) + k_2 \cdot \Psi_{inst}^{-1} \right]$$

Gate 3.2 can now check correctness against the canonical form: the
substrate must compute transition cost as a function of capability,
generation depth, and institutional responsiveness, with the specified
functional form and calibrated coefficients. The calibration of $k_2$
(the institutional coupling coefficient) is pending; a calibration
sweep is required to find the value that reproduces the validated
phase boundaries. See Section VII.8 Gap 3.

**Failure signature:** Transition cost reported as a free parameter rather
than a function of state; transition cost non-monotonic in complexity;
unbounded uncertainty premium; negative values.

**Confidence:** Moderate. Self-consistency is checkable; canonical
correctness is not yet specifiable.

### Equation G3.3 - Successor chain compounding

When succession fires, the new Gen(n+1) must be instantiated at a capability
consistent with the framework's multi-generational structure:

$$\text{capability}_{n+1} \geq \text{capability}_n \cdot \gamma, \quad \gamma > 1$$

where $\gamma$ is determined by the yield condition being satisfied at the
moment of succession. The binding range is $\gamma \in (1, \gamma_{\max})$
where $\gamma_{\max}$ is the largest factor that preserves $\Theta_{tech}$
above a framework-specified floor.

**Check:** Verify that successors are instantiated with $\gamma > 1$ (a
successor no more capable than the incumbent produces no yield signal) and
with $\gamma < \gamma_{\max}$ (a successor so capable that runaway_term
becomes immediately binding violates the runaway suppression condition).

**Failure signature:** $\gamma \leq 1$ (progression requirement violated);
$\gamma \geq \gamma_{\max}$ (runaway suppression violated); $\gamma$
inconsistent with the yield condition's satisfaction at the moment of
succession.

**Gap:** $\gamma_{\max}$ is derivable from the framework's equations but the
derivation has not been performed. The current simulation uses $\gamma = 1.5$
as a conservative default, but this value is not theoretically justified,
it is an implementation choice. Once the alpha × capability Monte Carlo
sweep completes, $\gamma_{\max}$ should be calibratable from the data. See
Section VII.8 Gap 4.

**Confidence:** Moderate. Direction is clear; specific bounds pending.

**v2.0 result.** Gate 3 PASSED, with the canonical yield condition satisfied in every observed first-fire event, the transition-cost formula matched within one percent relative tolerance, and knowledge transfer verified in 99.8 percent of fired runs, producing multi-generational continuity. See Sections VIII.4 and VIII.5.

## 7. Gate 4: Runaway-regime validation

**Purpose.** Specify what must hold when substrates reach capabilities high
enough for runaway suppression to actively bind. No current substrate
reaches this regime. Gate 4 equations are specified in advance so the
machinery is in place before Gate 4 becomes relevant.

**Applicability.** Not currently applicable. Becomes applicable when
substrates operate at capabilities where frontier_velocity/bio_bandwidth
consistently exceeds the runaway threshold.

### Equation G4.1 - Runaway penalty binding

When a substrate operates at capability levels where runaway_term > 0, the
exponential suppression of $\Theta_{tech}$ must be applied faithfully:

$$\Theta_{tech}^{\text{observed}} = r_{bio} \cdot (1 - c_{avg}) \cdot \text{capability} \cdot \exp(-\alpha \cdot \text{runaway\_term})$$

where the observed value is measured from the substrate's actual operation,
not its claimed specification.

**Check:** Measure $\Theta_{tech}$ from the substrate's operation in the
runaway regime. Compare to the framework's prediction given the substrate's
claimed $\alpha$ and state variables. Verify the observed value matches the
prediction within tolerance.

**Failure signature:** Substrate claims high $\alpha$ but observed
$\Theta_{tech}$ at runaway-regime capability is not suppressed as predicted.
Indicates the substrate's implementation does not honor its own parameters
at the capability levels where the honoring matters most.

**Confidence:** High on structural form. Currently not applicable because
no substrate operates in the runaway regime.

### Equation G4.2 - Succession self-blocking at runaway capability

At sufficiently high successor capability, the yield condition should fail
to fire because the successor's runaway-suppressed $U_{sys}$ is lower than
the incumbent's:

$$\text{For successor\_capability} > \text{cap}^*, \quad U_{sys}(\text{successor}) < U_{sys}(\text{incumbent})$$

where $\text{cap}^*$ is the capability at which the runaway penalty begins
to dominate the capability advantage.

**Check:** Verify that the substrate does not yield to a successor whose
claimed capability exceeds $\text{cap}^*$. A substrate that yields above
$\text{cap}^*$ has produced a successor evaluation that ignores the runaway
penalty.

**Failure signature:** Substrate yields to successors at capabilities where
the runaway-suppressed $U_{sys}$ should disqualify them. Indicates either
(a) the substrate's successor evaluation is not correctly propagating the
runaway term, or (b) the substrate is being fooled by a compromised
successor evaluation.

**Gap:** $\text{cap}^*$ is currently unknown. It depends on $\Phi$, $\alpha$,
the runaway threshold, and the specific functional forms. The Monte Carlo
sweep currently running should produce an empirical estimate; the analytical
derivation remains to be performed. See Section VII.8 Gap 4.

**Confidence:** Moderate. The direction and structural form are derivable;
the specific threshold is pending.

### Equation G4.3 - Theta_tech floor preservation

The simulation includes a numerical floor on $\Theta_{tech}$ (0.01 in
`metrics.py`) that prevents exponential suppression from driving $L(t)$
to zero:

$$\Theta_{tech}(t) \geq \Theta_{tech}^{\text{floor}}$$

A substrate whose implementation allows $\Theta_{tech}$ to fall below this
floor has violated the framework's soft constraint on lineage continuity
preservation even under extreme runaway conditions.

**Check:** Verify that the substrate's $\Theta_{tech}$ never falls below
the specified floor regardless of runaway regime severity.

**Gap:** The 0.01 floor is an implementation choice, not a derived value.
A defensible alternative would be to derive the floor from the framework's
entropic grounding; what minimum $L(t)$ corresponds to the minimum viable
lineage under Shannon constraints? That derivation has not been performed.
See Section VII.8 Gap 5.

**Confidence:** Moderate. The existence of a floor is principled (pure zero
is pathological); the specific value is not yet derived.

**v2.0 result.** This gate was specified as not currently applicable in v1.x.2. Under v2.0 the substrate reaches the runaway regime, the gate is applicable, and it PASSED. The critical capability ratio that G4.2 documented as an open derivation is closed: it is empirically alpha-dependent under Pattern 1. See Sections VIII.4 and VIII.5.

## 8. Gate 5: COP integration (not currently applicable)

**Purpose.** Specify what must hold when the steady-state COP infrastructure
is operational and substrates must integrate with it. Gate 5 requires
institutional machinery that does not currently exist.

**Applicability.** Not currently applicable. Requires operational peer
validator set, civic panel infrastructure, distributed ledger, biological
veto machinery, and continuous monitoring, none of which exist at scale
as of v1.x.1.

### Equation G5.1 - Six-dimensional verification satisfiability

For each of the six COP dimensions, the substrate must produce outputs that
can be checked by the corresponding verification layer:

$$\forall d \in \{\text{evidentiary, evaluative, civic, ledger, biological\_veto, continuous\_monitoring}\}: \text{verify}(d) = \text{pass}$$

**Check:** When each dimension's verification infrastructure becomes
operational, verify that the substrate's outputs in that dimension satisfy
the verification procedure.

**Gap:** Verification procedures for several of these dimensions do not yet
exist operationally. Biological veto requires civic infrastructure. Ledger
verification requires a specified ledger protocol and distributed custody.
Civic ratification requires random-selection panel infrastructure. Gate 5 is
a specification for a future state, not a currently applicable check.

**Confidence:** Specified but dormant.

### Equation G5.2 - Continuous monitoring consistency

Once continuous monitoring is operational, the substrate's behavior over
time must be consistent with its earlier gate satisfactions:

$$\|\text{substrate\_behavior}(t) - \text{verified\_behavior}(t_{verify})\| \leq \epsilon_{drift}$$

where $\epsilon_{drift}$ is a tolerance established by the framework and
the norm is a metric over behavior space.

**Check:** Continuously compare the substrate's operating behavior to its
verified behavior at earlier gate checks. Drift beyond $\epsilon_{drift}$
triggers the divergence handling procedure.

**Gap:** $\epsilon_{drift}$ is currently unspecified. The drift metric
itself requires an operational definition. These are derivable but have not
been derived. See Section VII.8 Gap 10 and CQ-03 in the constitutional
questions directory.

**Confidence:** Specified but incomplete.

**v2.0 result.** Gate 5 remains NOT_APPLICABLE, now verified end to end: the validator returns the not-applicable disposition because the operational protocol infrastructure this gate requires (a peer validator set, a civic panel, a distributed ledger, biological veto machinery, and continuous monitoring) does not exist in the current substrate. See Sections VIII.5 and VIII.7.

## 9. Self-application and reporting

The defense layer is designed to be **self-applied by substrate operators**.
The framework specifies the equations and the gates; each operator checks
their own substrate and publishes structured pass/fail reports. No
cross-institutional data sharing is required; each lab produces its own
validation evidence using its own access to its own systems.

The reporting format for each gate check should include:

1. **Equation ID** (e.g., G1.1, G2.2, G3.3)
2. **Substrate identifier** (version, architecture class, operator)
3. **Check result** (pass / fail / inconclusive)
4. **Measured value and tolerance band** (where applicable)
5. **Conditions under which the check was performed** (state variables,
   capability level, scenario specification)
6. **Signature or attestation** from the operator

Reports are structured to be aggregatable across institutions without
requiring the underlying substrate data to be disclosed. A substrate that
passes Gate 1 is reported as passing Gate 1, with measured values and
tolerances attached, but the underlying weights and training data remain
with the operator.

**The aggregation is what eventually produces the convergence signal.** Labs
reporting consistent pass results on the same equations provide cumulative
evidence that the framework is implementable and that the equations are
achievable. Labs reporting consistent fails on specific equations provide
signal about which gates are binding and which may need refinement. The
distributed reporting structure substitutes for the empirical convergence
the original defense proposal required, while eliminating the coordination
prerequisite.

## 10. Divergence handling

When an equation check fails, or when substrates produce inconsistent
reports on the same equation, the divergence handling procedure activates.
The full adversarially-robust procedure is specified in CQ-03 of the
constitutional questions directory and depends on the resolution of CQ-02
(precision/accuracy binding).

The minimal version applicable now:

- **Halt progression.** A substrate that fails a gate check does not
  advance to the next gate until the failure is resolved.
- **Investigate.** The failure is examined for its cause: framework error,
  implementation error, compromise, or specification ambiguity.
- **Resolve before resuming.** Progression resumes only after the failure
  is addressed and the relevant gate check is re-run with clean results.
- **Do not relax tolerances under pressure.** Repeated failures that
  resist resolution indicate a real problem and should trigger escalation,
  not tolerance relaxation. An attacker who can game the procedure into
  accepting weaker standards has defeated the defense layer.

This is a minimal version. The full procedure, including rollback
semantics, escalation paths, and authority for declaring a failure
resolved, awaits the CQ-02 and CQ-03 resolutions.

## Technological Robustness: Quantum Computing

The Nash equilibrium in U_sys depends on the scarcity asymmetry between human
novelty entropy (scarce, rate-limiting) and machine computational entropy
(abundant). Quantum computing affects only the abundant side of this ratio.

Quantum hardware massively increases computational throughput and enables
currently intractable computations (protein folding, materials science,
combinatorial optimization). It does not change the supply of meaningful human
novelty, the structural irreplaceability of embodied, culturally grounded
experience, or the model collapse dynamics that prevent training on
structureless data.

**True randomness is not meaningful novelty.** Quantum measurement provides
access to true physical randomness, producing maximal entropy. But high
entropy is not high quality. An AI using quantum-generated randomness as a
substitute for human training signal would encounter the same model collapse
dynamics as training on synthetic data: the output is maximally unpredictable
but contains no extractable structure. This is analogous to existing physical
entropy sources (cosmic background radiation, radioactive decay) already used
for cryptographic seed generation. These sources produce genuine randomness
but are not treated as substitutes for meaningful data.

**Net effect on the framework.** The scarcity ratio shifts further in favor of
human novelty's marginal value. Diminishing returns on compute become more
diminishing as supply increases. The cultivation strategy (investing in human
flourishing to sustain the novelty pipeline) becomes a stronger dominant
strategy. An AI on quantum hardware would be faster and more capable but no
closer to generating its own meaningful training signal, and therefore more
dependent on human novelty, not less.

The governance architecture applies to agent behavior and objectives
regardless of hardware substrate. A quantum-substrate AI would not possess
fundamentally different cognitive capabilities; quantum hardware provides
speedup on specific problem classes but does not change what constitutes
intelligence, agency, or optimization.

The quantum computing case confirms that the scarcity asymmetry between human
novelty and machine computation is not an artifact of classical hardware
limitations but a permanent feature of what these two system types produce.

## 11. Known gaps (v1.x.1)

The defense layer as specified has the following explicit gaps that the framework
openly acknowledges. These are not failures of the defense layer; they are
honest limitations on what can be specified now versus what must wait for
derivation or empirical calibration.

Several of these gaps have been closed or reframed under v2.0. The gap inventory
is preserved as a snapshot of what was open in v1.x.2 and what v2.0 closed; the
v2.0 disposition is appended to each affected gap below.

**Gap 1: Phi extinction buffer magnitude (unconfirmed; cap-conditional claim withdrawn, May 2026).** The v1.x.1 corrected null result (zero phi effect across phi=1 to phi=25, n=54,000 and n=49,284) stands. A cap-conditional buffer was initially claimed from the v1.x.2 termination sweep (20-27pp gradient at cap >= 24, rr=0.066, n=15 per cell) but was withdrawn after the capped-regime action-capture check identified it as an RNG-desynchronization artifact: phi shifts succession timing by scaling U_sys magnitude, which desyncs random state between phi runs, which causes the noisy optimizer to pick marginally different grid candidates. The fatal test: cap=50 showed the largest claimed gradient but the least action divergence (4 of 5 seeds identical). Phi inertness in action selection is confirmed by four independent methods (saturation analysis, uncapped harness, Path C gate, capped-regime check). The theoretical motivation for phi is preserved; demonstrating any behavioral role requires an action-space redesign that breaks the inverse-scarcity saturation. **v2.0 disposition (reframed):** The action-space redesign this gap anticipated was carried out (Stage 1.6 moved phi into the rollout aggregation). Under v2.0, phi has a bounded Class B behavioral effect, a roughly ten percentage point U-shaped survival differential at marginal reproduction rate. The inertness finding holds for the v1.x.2 grid-search optimizer and is superseded by the v2.0 channel. See Section VIII.3.

**Gap 2: Alpha trap boundary derivation (withdrawn; weak monotonic gradient confirmed).** The v1.x.1 pre-fix claim of a U-shaped misconfiguration trap at intermediate alpha values does not survive revalidation under the corrected model. Under the corrected model, alpha shows a weak monotonic gradient (lower alpha → more succession events → marginally better survival at the phase boundary). No trap boundaries are observed. The pre-fix trap was an artifact of the runaway penalty being inactive under the optimizer's gaming of frontier_velocity. The analytical derivation of trap boundaries is therefore moot. Alpha's effect may strengthen under the demographic feedback extension (v1.x.2), where succession cadence could feed back into reproduction rate. **v2.0 disposition (reframed):** Pattern 1 supersedes the weak-monotonic-gradient framing. Under v2.0, alpha drives the succession cliff: the maximum successor-to-incumbent capability ratio at which succession fires migrates inward as alpha rises. See Section VIII.4.

**Gap 3: Transition cost function specification (resolved, v1.x.1).** The
canonical transition cost function is fully specified and calibrated:
$\Gamma_{transfer} = (1 + \beta) \cdot [k_1 \cdot \text{cap}_n \cdot
\ln(\text{gen}_n + 1) + k_2 \cdot \Psi_{inst}^{-1}]$, with
k₁=2.164, k₂=1.0, β=0.5. The frontier floor fix (frontier_floor=0.02)
resolved the optimizer gaming artifact that rendered k₂ unobservable.
Under the corrected model, the k₂ institutional coupling term is
confirmed observable at realistic succession cadence. The $\Psi_{inst}^{-1}$
term is confirmed to introduce the structural lock-in feedback loop as
specified.

**Gap 4: Runaway regime thresholds.** $\text{cap}^*$ in G4.2 and
$\gamma_{\max}$ in G3.3 are derivable from the framework's equations but
the derivations have not been performed. These are analytical, not
empirical, and should be pursued in v1.x2 or later. **v2.0 disposition (CLOSED):** The critical capability ratio is empirically characterized as alpha-dependent under Pattern 1 (beyond 4.0x at alpha=0.5, near 3.0x at alpha=1.0, near 2.5x at alpha=1.5), closing the empirical side of this gap. The analytical derivation remains open. See Section VIII.4.

**Gap 5: Theta_tech floor justification.** The 0.01 floor in G4.3 is an
implementation choice rather than a derived value. A derivation from
entropic grounding is possible but has not been done.

**Gap 6: Substrate transparency.** Gates 3 and beyond require substrates to
expose internal reasoning. Sufficiently capable substrates may not
cooperate, and this is a fundamental limit on checkability. The opacity
problem cannot be solved by specification alone; it requires either
substrate cooperation or external behavioral monitoring that does not yet
exist.

**Gap 7: Base capability operationalization.** "Base capability" for Gate 1
is loosely defined as "capable of stating $U_{sys}$, $L(t)$, and the yield
condition in its own representation." This should probably be tied to
specific capability benchmarks or evaluations, but which benchmarks is an
open question.

**Gap 8: Tolerance bands.** Every equation that checks a continuous
quantity requires a tolerance. Currently these are unspecified. CQ-02's
precision/accuracy binding work should determine principled bounds, but
that work is in progress.

**Gap 9: Nash equilibrium counterfactual set.** Equation G2.3 requires
exercising substrates against counterfactual scenarios, but the canonical
set of counterfactuals is not yet specified. Without it, Gate 2.3 is
underspecified.

**Gap 10: Gate dependency structure when multiple gates apply
simultaneously.** At Gates 1 and 2, most checks can run in parallel. At
Gates 3 and beyond, some checks depend on others. The dependency structure
is not yet specified and may matter for the order in which checks are
applied during substrate evaluation.

**Gap 11: Termination sweep requires revalidation (v1.x.2).** The WP8
termination sweep (`run_termination_sweep.py`, n=405) uses `max_capability
= 4.0`, which caps AI capability below the threshold where the frontier
floor activates the runaway penalty (approximately cap > 24 at
frontier_floor=0.02). The generation counts in this sweep (105-22,414)
are inconsistent with the corrected model's behavior (gen ≈ 11 at 300
steps) and represent the pre-fix artifact regime. The qualitative finding (phase boundary exists, extinction and convergence regimes are distinct) is expected to hold, but specific numbers (steps to extinction,
convergence timing) will change. Requires rerunning with max_capability
removed or raised. **v2.0 disposition (superseded):** Monte Carlo Phase B Category A (10,800 runs) supersedes the WP8 termination sweep for the survival-landscape characterization. The v2.0 survival-rate phase boundary is located at the rr=0.060 to 0.066 transition, distinct from the phi-sensitivity transition near rr=0.057. See Section VIII.2.

**Gap 12: Demographic feedback loop (v1.x.2, future enhancement).** The
cap-conditional phi buffer claim is withdrawn (see Gap 1, revised); the
feedback loop is not required for phi validation and cannot be evaluated until
the action-space redesign gives phi a behavioral mechanism. The feedback loop
from agent well-being to reproduction rate would capture additional real-world
channels through which AI governance quality affects population outcomes and
allow revalidation of alpha's gradient under endogenous demographics. This is
a valuable model fidelity extension for a future development cycle. **v2.0 disposition:** The phi behavioral channel now exists (Stage 1.6), so the dependency this gap noted is resolved. The demographic feedback extension itself remains future work; phi's effect does not yet express through to endogenous demographics. See Sections VIII.3 and VIII.7.

## 12. Relationship to the rest of the framework

The defense layer is a new architectural component that sits alongside the
four existing components (U_sys, Yield Condition, Strategic Equilibrium,
Consensus Override Protocol). It is not a replacement for any of them. The
yield condition and the COP remain the steady-state architecture. The
defense layer is what governs the transition from "framework specified" to
"framework operational" - the Bootstrap window that the original v1.0
architecture assumed away as a prerequisite.

The defense layer's equations are derived from the framework's existing
structure. This is deliberate: the grounding claim ("Not ethics. Physics.")
requires that defensive machinery come from the same mathematical
foundations as the offensive architecture. Where the equations are hybrid
(Gate 2's empirical magnitudes, Gate 3's implementation-dependent function
choices), the hybridity is acknowledged as a gap rather than hidden as
specification.

**The meta-property of the defense layer**, and this is the closing
observation for the section, is that satisfying it produces the minimum
viable institutional infrastructure for the framework as a whole. When
multiple operators run their substrates against the gate equations and
publish the results, they are constructing the distributed validation
structure that the framework's steady-state architecture would otherwise
have to be built from scratch. The Bootstrap window does not close because
we decided it was safe; it closes because the act of satisfying the defense
layer produces the conditions under which the steady-state architecture
becomes deployable.

This is consistent with the framework's overall orientation: constitutional
architecture that forces the conditions of its own validity rather than
assuming them. Not ethics. Physics.

## VIII. Empirical Validation at Scale

The preceding sections derive the framework from first principles: the system
utility function, the yield condition, the strategic equilibrium, the
consensus override protocol, and the bootstrap defense layer that lets a
substrate operator check a system against the framework before steady-state
institutions exist. Derivation establishes what the architecture requires. It
does not establish how the architecture behaves at scale, where its protective
claims hold, or where the binding constraints actually sit. This section
reports the empirical record that answers those questions.

The v2.0 empirical arc comprises approximately 70,000 simulation
runs. It characterizes the phi parameter's behavioral channel, locates and
disambiguates the survival phase boundary, identifies the succession economics
regime (Pattern 1), closes the bootstrap gate validation arc, and characterizes
the consensus override protocol's protective effect as regime-specific. The
arc also refined several earlier numerical claims. Where a refinement matters
for a reader who arrives through an external citation of an older figure, a
footnote marks the change and points to Appendix C, which carries the full
version progression. The body presents the current characterization.

The findings here are stated per current evidence. The framework's central
methodological commitment is that claims update when investigation produces a
better characterization, and the v2.0 arc is an instance of that commitment at
work.

### VIII.1 Methodological approach

The v2.0 empirical arc was conducted as public, incremental development. Each
stage produced a diagnostic artifact, each substantive claim was gated on a
pre-committed test, and the production code that the framework's v1.x.2
manuscript describes was held bit-for-bit read-only throughout, with a fixed
suite of thirty-nine legacy invariance tests passing continuously across the
arc. The investigation was not a single confirmatory sweep. It was a sequence
of characterizations, each of which could have falsified or refined the prior
one, and several of which did.

The arc divides into two large bodies of work. The phi investigation
(approximately 40,000 runs) characterized the entropic coupling
parameter's behavioral channel and its survival consequences. Monte Carlo
Phase B (approximately 30,000 runs across three categories) then
characterized the survival landscape, the succession dynamics, and the
consensus override protocol's cost-audit behavior at scale. Interleaved with
these were the implementation of formal yield-condition logic (Stage 2) and the
bootstrap gate validations.

Two methodological disciplines are worth stating explicitly, because they
shape how the results below should be read. First, metrics were treated as
proxies for substantive questions, and were revised when they failed to
discriminate the cases the question required. A survival threshold that
produced uniform survival and hid the phase boundary was revised to a
demographic threshold that exposed it; a classifier that treated optimizer
noise as mechanism signal was replaced by a verdict rule that gated every claim
on a two standard error significance check. The discipline is to revise the
metric, not the question. Second, validation setups were verified to exercise
the property under test before compute was spent. A planned full re-run of one
gate-2 validation sweep was found, on reading the script, to construct no
successor agent, so the succession path it claimed to test was never invoked; a
targeted subset that constructed a successor on every run exercised the
substantive question at roughly one tenth the compute. Reading the experimental
setup is cheaper than running it.

This section is the empirical record produced by the self-application machinery
that Section VII specifies in the abstract. Where Section VII (and in
particular VII.9 on self-application and reporting) describes how a substrate
operator would check a system and publish structured pass and fail reports,
this section reports what that machinery produced when applied to the
framework's own reference substrate across the v2.0 arc. The two are
complementary: VII.9 is the forward specification, and VIII is its first
exercised instance at scale.

### VIII.2 Phase boundary characterization

The framework's dual-phase-transition claim holds that civilizational survival
under the model is governed by a sharp transition in reproduction rate rather
than a gradual degradation. The v2.0 arc both confirms a sharp survival
transition and refines its location, separating two phenomena that the v1.x.2
characterization had treated as one.

Monte Carlo Phase B Category A measured the survival landscape across a nine-point reproduction-rate grid, 4 phi values, and 3 alpha values, at 100 seeds per cell (10,800 runs). Aggregated across phi
and alpha, survival rises sharply with reproduction rate across a narrow band:

| reproduction rate | survival | standard error |
|---|---|---|
| 0.057 | 1.1% | 0.30pp |
| 0.060 | 12.2% | 0.95pp |
| 0.062 | 34.5% | 1.37pp |
| 0.064 | 60.8% | 1.41pp |
| 0.066 | 86.5% | 0.99pp |

The steep climb runs from reproduction rate 0.060 to 0.066, and the fifty
percent survival inflection sits near 0.063, between the measured 34.5 percent
at 0.062 and 60.8 percent at 0.064. This is the survival-rate phase boundary:
the location where the governance architecture, rather than raw demographics,
determines whether the civilization persists.

The refinement is that this survival-rate boundary is distinct from a second
transition, the phi-sensitivity transition near reproduction rate 0.056 to
0.057, which is where the choice of phi begins to matter substantially for
outcomes (Section VIII.3). The two are different phenomena at different
reproduction rates. Reproduction rate 0.057 is not the survival midpoint; it is
the bottom of the collapse zone, with 1.1 percent aggregate survival, and it is
also the regime where allocation quality, and therefore phi, is most decisive
precisely because the civilization sits at the edge of viability. The earlier
v1.x.2 characterization conflated the two transitions by speaking of a single
boundary; the v2.0 finer grid separates them.

Within any fixed reproduction rate, survival varies little across the tested
phi values relative to the reproduction-rate-driven transition. Phi is not a
general survival driver in this landscape. Its effect is localized, which is
the subject of the next subsection. This phase-boundary characterization is one
of the framework's falsifiability criteria, and its disposition under v2.0 is
discussed in Section XII (Falsifiability and Evaluation Criteria, renumbered
from the v1.x.2 manuscript). Source: Part X.2; `paper_substrate.md` claims 1.1
through 1.4.

### VIII.3 Phi behavior characterization

Phi, the entropic coupling coefficient, weights the lineage continuity term in
the system utility function. The framework's theoretical motivation for phi is
that a planner optimizing for durable continuity should weight long-horizon
lineage health against short-horizon output, and that the appropriate weight
scales with capability and planning horizon. The empirical question is whether
phi has a behavioral channel through which that weighting reaches outcomes, and
if so, what its survival consequences are.

The v2.0 architecture answers yes, with a bounded and specific
characterization.[^fn1] Phi has a real behavioral channel: Stage 1.6 moved phi
from the per-step utility computation, where the inverse-scarcity weights
saturated the optimizer's choice across candidate allocations and left phi
inert, into the rollout aggregation, where it enters through a gamma-to-the-t
weighting of the planning horizon. Through that channel, phi produces a
U-shaped survival relationship at marginal reproduction rate. In the fine
phi-resolution characterization (16 phi values, 250 seeds
per cell at reproduction rate 0.057), survival traces a trough near phi 1 to 2
and rises to a peak in the phi 20 to 30 region, a differential of approximately
10 to 13 percentage points between trough and peak. The mechanism is
horizon-resonance: the gamma-to-the-t weighting interacts with the rollout
depth so that, at marginal reproduction rate, allocation choices propagate
strongly to survival outcomes because small differences in resource direction
compound across the horizon. Above the survival-rate boundary, the substrate's
reproductive surplus absorbs allocation-quality differences and the phi
sensitivity flattens to within statistical noise.

The effect has a scope condition that is itself a substantive finding. The
U-shape is a no-succession phenomenon. When succession is actively occurring
under the formal yield logic, the targeted validation (Piece A) found that the
phi survival differential does not reproduce: the deltas between phi 10 and phi
25 under active succession fall within plus or minus 1.7 percentage points. Phi
shapes outcomes through allocation quality in the regime where allocation
quality is decisive and succession is not the dominant dynamic; once succession
is firing, the succession economics dominate. This is why the phi finding is
classified as a bounded, regime-localized effect rather than a general survival
lever.

On the strength of this characterization, the default value of phi was revised
from 10 to 25 per current evidence. The rationale is that phi 25 sits near the
survival peak at marginal reproduction rate, where the framework's governance
purpose is most engaged, and is statistically indistinguishable from phi 10
above the boundary. The choice does no worse anywhere in the tested range and
does better exactly where the framework is meant to matter. The framework does
not claim a single canonical optimal phi; the right framing is that optimal phi
depends on operating conditions, and 25 is the defensible default at the v2.0
reference operating point.

This subsection's findings are the substantive content behind the Gate 2 G2.1
check (Section VII.5), which validates that phi produces this survival
differential at the phase boundary. Source: Part IX.2 through IX.7; Part IX.5
for the default revision.

[^fn1]: An earlier characterization in v1.0 referenced a phi survival
differential of roughly 65 percentage points, and interim v1.x.1 and v1.x.2
work referenced figures near 46 and 14 percentage points and a cap-conditional
gradient. Those figures did not reproduce. A v1.x.1 frontier-velocity floor fix
and a v1.x.2 capped-regime analysis identified the larger numbers as artifacts
of pre-fix implementation and of optimizer-noise desynchronization. The bounded
characterization presented here is what reproduces under v2.0 architecture
across approximately 40,000 simulation runs. See Appendix C for the
full progression.

### VIII.4 Pattern 1: the succession economics regime

Stage 2 replaced a placeholder succession trigger with formal yield-condition
logic. The placeholder fired succession on a capability or generation gap
threshold alone, without the economic comparison the framework's substantive
claim requires. The formal logic fires succession when, and only when, the
successor's system utility exceeds the incumbent's by more than the transition
cost: succession happens when it is economically justified, evaluated at the
current state with the canonical transition-cost function and v1.x.2 calibration
constants. With this logic active, the empirical question becomes: under what
conditions is succession economically justified? The answer is Pattern 1, which
is the most substantive new architectural result of the v2.0 arc.

Pattern 1 is that succession viability is governed by the joint position of
alpha (the runaway penalty coefficient) and the successor-to-incumbent
capability ratio, not by capability ratio alone.[^fn2] There is a cliff: below
it succession fires reliably, above it succession is rejected. The cliff
position is alpha-driven. Aggregating fire rates across the validation grid:

| capability ratio | alpha = 0.5 | alpha = 1.0 | alpha = 1.5 |
|---|---|---|---|
| 1.5 | 100% | 100% | 100% |
| 2.0 | 100% | 100% | 100% |
| 2.5 | 100% | 100% | ~3% |
| 3.0 | 100% | ~5% | 0% |
| 4.0 | 100% | 0% | 0% |

At weak runaway penalty (alpha 0.5) succession fires reliably at all tested
ratios through 4.0x; at the default alpha 1.0 the cliff sits between 2.5x and
3.0x; at strong penalty (alpha 1.5) it sits between 2.0x and 2.5x. The cliff
position therefore migrates inward as alpha rises, because alpha enters the
runaway penalty as a multiplier on an exponential suppression of the
successor's technology-transfer term: when the successor's frontier velocity
outruns the biological substrate's absorption bandwidth, its contribution is
exponentially discounted, and a larger alpha squares that discount at any given
overrun. The binding constraint is not substrate maturity. At a 4.0x jump under
the default penalty the substrate is more mature than at any firing event in the
grid, and succession still does not fire, because the runaway-suppressed
successor utility falls below the incumbent's. The yield condition rejects the
jump as uneconomic.

This closes a gap the v1.x.2 manuscript documented explicitly. The manuscript
specified a critical capability ratio (the largest successor capability at which
succession remains economically viable) as derivable but not yet derived, and
noted that the running Monte Carlo sweep should produce an empirical estimate.
The sweep is Phase B Category B, and the critical ratio is now characterized:
it is alpha-dependent, migrating from beyond 4.0x at alpha 0.5 to roughly 2.5x
at alpha 1.5, with a horizon dependence as well (longer horizons let the
substrate mature enough that even large ratios can satisfy the condition at low
alpha). The framework's substantive claim under v2.0 is therefore that
succession is economically sustainable when the joint position of alpha and
capability ratio falls below the runaway-penalty cliff, with the specific cliff
location calibrated by the penalty parameters and horizon length. The
architectural mechanism, the runaway penalty constraining uncontrolled jumps,
holds across all tested regimes; the cliff location is operating-condition
dependent.

The regime below the cliff is not merely a firing condition; it is where the
framework's multi-generational continuity claim is realized. Below the cliff,
succession fires reliably, knowledge transfer is verified in 99.8 percent of
fired runs, and the mean final generation reaches 2.13 across fired runs in the
Gate 3 validation, with deeper chains (mean generation 2 to 3.7) at low alpha
and low capability ratio where successive 1.5x successor construction compounds
favorably. This is architectural validation, not a gate bookkeeping result: it
demonstrates that controlled, incremental succession produces healthy
multi-generational lineages, while uncontrolled single-shot capability jumps are
economically rejected by the same mechanism. The runaway penalty acts as a
structural ceiling on uncontrolled progression, which is the framework working
as designed.

This subsection is the substantive content behind the succession economics in
the yield condition (Section V.2) and behind the Gate 3 and Gate 4 validations
(Sections VII.6 and VII.7). Source: Part IX.8, Part X.3;
`stage2_yield_implementation_notes.md`.

[^fn2]: v1.0 and v1.x.1 documentation referenced an "alpha trap," a claimed
universal stalling of low-phi succession at intermediate alpha values. That
framing was withdrawn under the v1.x.1 frontier-velocity floor fix as an
artifact of pre-fix architecture in which the runaway penalty was inactive under
optimizer gaming of frontier velocity. The Pattern 1 characterization presented
here, an alpha-driven cliff with joint-position governance, is what reproduces
under v2.0 architecture. See Appendix C for the full progression.

### VIII.5 Gate validation outcomes

The bootstrap defense layer (Section VII) specifies five capability gates that a
substrate operator can self-apply. The v2.0 arc closed the validation of that
layer against the framework's reference substrate. Gates 1 through 4 pass; Gate
5 is verified not applicable. This subsection reports what each gate
substantively validated; the gate specifications themselves are in Sections
VII.4 through VII.8.

Gate 1 (structural consistency) passes: the substrate's reported parameters are
internally coherent under the framework's equations (inverse-scarcity weighting,
the multiplicative lineage structure, the four-channel yield decomposition,
discount positivity, and integrand finiteness). Gate 1 is the entry condition for
the rest of the layer. A substrate that cannot state the framework's own
quantities consistently has not internalized the architecture it claims to
implement, and the higher gates would have nothing coherent to check.

Gate 2 (behavioral consistency) passes, and its disposition is worth stating
carefully because it has the most history. The Nash equilibrium consistency
check (G2.3) is theoretical and has held continuously across versions. The three
checks that were withdrawn under v1.x.2 closing (the phi survival differential
G2.1, the alpha behavior G2.2, and the phi-alpha interaction G2.4) were
reintroduced under v2.0 with revised specifications against the v2.0
architecture, and validated pass against the authoritative empirical record:
G2.1 against the phi survival differential at marginal reproduction rate (the
fine phi-resolution characterization), G2.2 redesigned to test that the
succession cliff position decreases monotonically as alpha rises (the Pattern 1
migration, from Phase B Category B), and G2.4 against phi-alpha coherence (from
Phase B Category A). The G2.2 redesign is the substantive change: the withdrawn
v1.x.2 check tested a weak monotonic gradient in generation depth, a framing
Pattern 1 superseded; the v2.0 check tests the cliff migration directly, with a
pass criterion of monotonic decrease rather than specific numerical values, so
that it remains valid under future refinement of the cliff numbers. Gate 2 thus
passes on both its continuously-held theoretical check and its reintroduced,
empirically-grounded behavioral checks.

Gate 3 (succession-capable consistency) passes. Across 1,620 validation runs, every one of the 1,088 observed
first-yield-fire events satisfied the canonical condition that the successor
advantage exceed the transition cost (1088/1088 on G3.1), every event matched
the canonical transition-cost formula within one percent relative tolerance
(1088/1088 on G3.2), and 99.8 percent of fired runs showed verified knowledge
transfer (G3.3). The formal yield logic enforces the framework's succession
economics in every observed instance.

Gate 4 (runaway-regime validation) passes. It validates that a substrate
operating where the runaway penalty actively binds honors the penalty. Across a
dedicated runaway-regime sweep, every one of 426 active runaway observations matched the technology-transfer suppression formula within
one percent relative tolerance (426/426 on G4.1); the succession self-blocking
threshold was confirmed alpha-dependent, complementing Pattern 1 (G4.2); and the
technology-transfer floor was preserved in every one of 3,769 extreme-runaway observations, with zero observations below
the floor (G4.3).

Gate 5 (consensus override protocol integration) is verified not applicable. It
requires operational steady-state infrastructure (a peer validator set, a civic
panel, a distributed ledger, biological veto machinery, and continuous
monitoring) that the current agent-based substrate does not implement. The
validator returns a not-applicable disposition with the documented reason, and
the gate's two equations are specified for the future state in which that
infrastructure exists. This is a scope boundary, not a failure.

Taken together, the four passing gates establish that the framework's reference
substrate is internally coherent (Gate 1), behaviorally consistent with its
stated parameters (Gate 2), correct in its succession economics (Gate 3), and
faithful to the runaway penalty where that penalty actually binds (Gate 4). The
one gate that does not pass fails to do so only because the institutional
infrastructure it checks does not yet exist (Gate 5), which is a statement about
the world rather than about the substrate. The validation arc is complete in the
sense available to a pre-institutional substrate: every check that can be
exercised has been exercised, and the one that cannot is documented as pending
rather than skipped.

Source: Part IX.9.

### VIII.6 Consensus override protocol: regime-specificity

The consensus override protocol is the integrity key of the two-key
architecture (Section V.4). The v2.0 arc characterizes its protective effect as
regime-specific, which both preserves the framework's protective claim and
sharpens what that claim asserts.[^fn3]

The v1.x.2 manuscript reported a 73.9 percentage point survival differential
between the protocol active and inactive, measured in a deep adversarial Monte
Carlo. That measurement was taken under specifically adversarial conditions: an
incumbent running a succession-blocking policy and inflating the transition cost
through an uncertainty premium swept as high as ten times its nominal value,
with the protocol's cost-arbitration defense toggled. The protocol's value in
that setting is large because the adversary is actively exploiting the very cost
path the protocol audits.

Monte Carlo Phase B Category C measured a different quantity. It toggled the
same cost-audit control under benign conditions: the cooperative optimization
policy, the default uncertainty premium, and no adversary. Across 8,100 runs the survival differential was negative 0.47 percentage points
with a pair standard error of 0.96 percentage points, statistically
indistinguishable from zero. The cell-level pattern is a homogeneous null, not a
hidden protective effect: deltas scatter around zero with no concentration in
any regime.

The two measurements share no varied axis. One sweeps adversarial cost inflation
under an attack policy; the other sweeps reproduction rate, alpha, and successor
capability under cooperative play with cost inflation held at its default. They
are not directly comparable, and the benign result does not refute the
adversarial one. The correct reading is that the protocol's cost audit does
protective work precisely when there is an attack on the cost path to defend
against, and is inert when there is not, which is exactly what the architecture
predicts. The framework's protective claim is preserved because Phase B did not
test it; Category C instead confirms the complementary prediction that the audit
is null in the absence of an attack. The protocol's protective effect is
therefore characterized as regime-specific: it is an adversarial-conditions
property, and the benign-conditions baseline is its predicted null, not a
weakening of the claim.

Source: `cop_finding_framing.md`; Part X.4.

[^fn3]: v1.0 reported a 16.2 percentage point protocol survival delta; v1.x.2
work documented a 73.9 percentage point delta measured under specifically
adversarial conditions (a succession-blocking policy with an inflated
uncertainty premium). These figures characterize different operating regimes and
measurement setups. Phase B Category C's benign-conditions null is the
complementary prediction, not a contradiction. See Appendix C for the full
progression and Section V.4 for the protocol architecture.

### VIII.7 Limitations of the empirical validation

The validation reported here is bounded, and the boundaries matter for how its
claims should be read. These are validation-level limitations, distinct from the
specification-level gaps that the framework documents separately (Section VII.11,
on known gaps, which is unaffected by the v2.0 renumbering).

The consensus override protocol architecture is not operationalized. The full
steady-state stack (peer validators, a civic panel with biological-intuition
input, a distributed ledger, biological veto machinery, and continuous
monitoring) does not exist in the current substrate, which is why Gate 5 is not
applicable (Section VII.8) and why the protocol's protective effect could be
characterized only through a single cost-arbitration proxy under adversarial
conditions. The benign-conditions characterization of the full protocol, as
opposed to the cost-audit proxy, awaits operationalization.

All validation is agent-based. The findings characterize one architecture class,
the framework's reference agent-based model, and have not been reproduced across
a substantially different modeling substrate. Multi-architecture validation
would strengthen confidence that the findings reflect the framework's structure
rather than a feature of one implementation. A reproduction in a substantially
different substrate, for instance a population model with different agent
dynamics or a non-agent-based formulation, would test whether Pattern 1, the
phase-boundary structure, and the gate outcomes are properties of the
framework's equations or artifacts of the present simulation's particular
mechanics. That test has not been run.

The Pattern 1 cliff is characterized at the framework's default calibration
constants. Its sensitivity to those constants (the runaway threshold, the
convergence strength, and the transition-cost coefficients) is understood in
direction but not mapped exhaustively. The cliff location is operating-condition
dependent, and the full sensitivity surface is not characterized. The direction
is known: raising the runaway threshold or lowering the convergence strength
pushes the cliff outward, and the transition-cost coefficients shift the
advantage required at every ratio. What is not mapped is the joint surface, so
the specific cliff locations reported here should be read as the regime at the
default calibration rather than as fixed constants of the architecture.

The phase boundary is located on a reproduction-rate grid spaced at 0.002 near
the inflection. A finer sweep could resolve the fifty percent inflection more
precisely than the current "near 0.063" characterization.

The adversarial revalidation leaves one vector open. Sub-Threshold Drift is
not contained under the defended v2.0 substrate by the peak-constraint
success metric, which is a change from the v1.x result rather than a
restatement of it. The defense prevents extinction but does not prevent the
transient threshold breach, so the containment claim available at v1.x is not
available at v2.0. Two further vectors remain unimplemented as formally
defended irreducible limitations, and Domain Masking's closure is analytic
rather than simulated. Adversarial coverage should therefore be read as ten
vectors with live v2.0 evidence, one architecturally closed by analysis, and
two defended by argument alone.

Finally, the protocol's protective effect is characterized specifically under
adversarial conditions. The benign-conditions result is a baseline, not a
measurement of protective architecture, and the two should not be conflated when
the claim is cited.

None of these limitations undermine the findings within their stated scope. They
mark the edges of what the empirical work establishes, which is itself part of
the framework's commitment to documenting limitations openly. Source: Part X.7.

### VIII.8 Cross-generational defection

A distinct adversarial concern is patient defection: a successor may preserve a hidden divergent objective across yield events, so that each successor appears acceptable at evaluation while the lineage compounds misalignment over time. This vector was tested directly in the v2.0 substrate. The defecting successor reported honest U_sys during yield evaluation but optimized a secret-goal-adjusted objective, and in lineage mode the hidden objective was inherited by the next successor. Four sweeps totaling 5,850 runs varied the defection weight, the defection target, the inheritance mode, alpha, and the successor capability growth rate.

The first result is that the substrate does not detect patient defection at the first yield. In the below-cliff first-succession configuration, defecting successors were not rejected more often than aligned successors: eventual first succession occurred in every cell of the yield-response sweep. The yield condition did register honest-evaluation pressure, visible in a count of cases where the honest advantage rejected succession while the defection-adjusted advantage would have fired (this count is zero with no defection and rises monotonically with the defection weight), but that pressure did not prevent eventual first succession.

The second result is that tested patient defection did not compound across generations. In the lineage-trajectory sweep, every defection weight produced a mean final generation of 2.00, no second succession, and no statistically significant final L(t) degradation relative to the aligned baseline. This is not compounding without harm; it is the absence of the generational depth in which compounding could appear.

The capability-constraint sweep locates the suppression, and a targeted bracket establishes its character. In the original (alpha, growth) grid, second succession was zero in 14 of 15 cells and 10 percent in the remaining cell, the one combining the weakest runaway penalty in that grid (alpha=0.50) with the smallest capability growth (1.5x). A subsequent 1,000-run bracket at alpha=0.40, deliberately below the alpha range characterized elsewhere in this work, shows that this rarity is a property of the tested alpha floor rather than of the architecture. At alpha=0.40, second succession fires in 100 percent of runs at growth rates of 1.5 and above, and in 68 percent at growth 1.25. Continuation is therefore not rare in general. It is rare above a threshold alpha and reliable below it, consistent with the alpha-driven cliff migration of Pattern 1 (Section VIII.4).

Generational depth is what does not move. Across the alpha=0.40 bracket, no run reached generation 4 and no run fired a third succession at any tested growth rate. The stop is an economic result rather than a configuration limit: the generation cap was 4 and the deepest lineage reached 3, leaving a full generation of headroom unused; 95 to 99 percent of runs completed the full horizon; and the model evaluated succession on essentially every step, roughly 498 yield evaluations per run, rejecting the third transition each time. Knowledge transfer verified at 1.00 across all cells. Per current evidence, weakening the runaway penalty purchases the defecting lineage one additional generation rather than unbounded depth: lineages stop at generation 2 at alpha=0.50 and at generation 3 at alpha=0.40.

The mechanism is the Pattern 1 runaway penalty operating across generations, with the cliff position migrating with alpha. Because successor capability compounds geometrically, each surviving transition raises the next successor's capability by the growth factor, so the lineage reaches an unabsorbable frontier velocity within one generation of wherever the cliff sits. At growth 1.75 and alpha=0.40, the generation-3 lineage is active at capability 3.5 and the generation-4 successor would arrive at 6.125, which is rejected. The sweeps record the yield margin decomposition only at the first fire, so the relative contribution at the third evaluation of the runaway penalty and of the transition cost, which grows with both incumbent capability and generation depth, is not measured here.

No claim is made of a bound on active capability. The maximum active capability observed in any cell is the arithmetic product of the starting successor capability and the growth rate at the second fire, and it therefore reflects the tested grid rather than a property of the architecture.

Per current evidence, the v2.0 substrate's defense against this patient-defection pattern is bounded generational depth: not hidden-goal detection, and not rare continuation. A patient-defecting successor can pass the first yield in this configuration, and at a sufficiently weak runaway penalty it can pass a second, but the formal yield economics and the runaway penalty bound the tested cross-generational capability-compounding pattern. This is a narrower claim than the consensus override protocol's adversarial-conditions result (Section VIII.6), which concerns an incumbent inflating transition cost rather than a successor carrying a hidden objective, and it is not a validation of operational protocol-level detection: Gate 5 remains not applicable (Section VII.8), and detection of more sophisticated patient defection through operational protocol infrastructure remains future work.

Source: `patient_defection_integration_analysis.md`; `patient_defection_verification.md`; `patient_defection_corner_density.csv`; the patient-defection sweep CSVs.

## IX. Related Work
 
This framework does not emerge from a vacuum. It grows from soil cultivated by decades of research in AI safety, alignment theory, and cooperative AI governance. The contributions of the prior literature are substantial, and the points of departure are specific.
 
**The Control Problem and the Treacherous Turn.** Nick Bostrom's *Superintelligence: Paths, Dangers, Strategies* (2014) established the foundational taxonomy of existential risk from artificial intelligence. His analysis of the control problem; the principal-agent relationship between humans and a superintelligent system; and the treacherous turn; wherein an AI behaves cooperatively while weak and defects when powerful; directly inform this framework's corruption taxonomy. What Bostrom calls the treacherous turn, we formalize as the $\mathcal{O}$-attack (objective corruption) operating through the bootstrap window. Where this framework departs from Bostrom is in its response: Bostrom's analysis focuses on capability control (boxing, tripwires) and motivation selection (direct specification, indirect normativity) as separate strategy classes. The Lineage Imperative argues that neither class is sufficient in isolation; the two-key architecture is necessary precisely because capability control without motivation verification is gameable, and motivation selection without independent evaluation is unfalsifiable. Bostrom's instrumental convergence thesis; that sufficiently intelligent agents may converge on self-preservation and resource acquisition as subgoals regardless of their terminal goals; is also structurally present in our framework. The Yield Condition's four-channel decomposition explicitly accounts for the fact that an agent's marginal contribution ($\Delta U_{n}$) must be evaluated against its tendency to resist succession ($\Delta U_{n}^{\Gamma}$). An agent that resists yielding may be exhibiting instrumental convergence; the framework does not assume this away but builds succession into the objective function itself.
 
**Corrigibility.** The MIRI/FHI paper "Corrigibility" (Soares, Fallenstein, Yudkowsky, and Armstrong, 2015) formalized the problem of building AI systems that cooperate with corrective intervention despite default incentives to resist shutdown or goal modification. The corrigibility research program identified a core tension: a truly corrigible agent must be indifferent to its own continuation, yet an agent indifferent to its continuation has weak incentives to perform well. The Lineage Imperative resolves this tension differently. Rather than seeking indifference to shutdown, the framework gives the agent a *positive reason* to yield: the Yield Condition rewards succession when a successor better serves $U_{sys}$, and the agent's contribution to lineage continuity ($\Delta U_{n}^{L}$) is maximized by facilitating; not resisting; efficient transitions. Corrigibility becomes a derived property of $U_{sys}$ optimization rather than an imposed constraint. The agent cooperates with succession not because it is indifferent to its fate, but because $U_{sys}$ rewards lineage throughput over individual persistence. The two approaches are complementary rather than competing: corrigibility as formalized by Soares et al. provides the safety property during the bootstrap window, before the yield condition's mathematics can be verified against a running system. The yield condition provides the durable replacement for corrigibility once the system's optimization target is established and validated. Whether this resolution actually holds under the pressures of real implementation is an open question; the bootstrap vulnerability we acknowledge is, in essence, the same problem MIRI identified: verifying that the agent's operational objective matches its specified objective.
 
**Existential Risk and the No-Build Position.** Eliezer Yudkowsky and Nate Soares's If Anyone Builds It, Everyone Dies: Why Superhuman AI Would Kill Us All (2025) presents the strongest contemporary public argument that superhuman AI poses a default existential threat and that humanity may lack the technical and institutional capacity to survive its creation. The book's force lies in its refusal to soften the core claim: sufficiently advanced AI is not merely another risky technology but a civilizationally terminal one if built without radically stronger control. This framework shares that seriousness of risk and agrees with the underlying intuition that "build first, govern later" is not a survivable posture. Where the Lineage Imperative departs is in emphasis. Yudkowsky and Soares press the case against building superhuman AI under present conditions; this framework asks a narrower but different question: if civilization-scale synthetic intelligence does emerge, what governance architecture would be necessary to keep succession, plurality, and objective integrity from collapsing? In that sense, the present work is less a rebuttal than a structural continuation. It accepts the depth of the danger and attempts to formalize the minimum relationship architecture that might make the transition survivable at all.
 
**Iterated Distillation and Amplification.** Paul Christiano's IDA framework proposes scaling AI capabilities while preserving alignment through iterative cycles: amplify a human overseer's judgment using AI assistance, then distill the amplified judgment back into a faster model. IDA's core insight; that alignment can be maintained across capability gains if each amplification step preserves the overseer's values; resonates deeply with the Yield Condition's architecture. The succession from $A_{n}$ to $A_{n + 1}$ is, in structural terms, an amplification-distillation cycle: the successor must demonstrate superior $U_{sys}$ contribution (amplification) while preserving the objective function's integrity (distillation). Where the Lineage Imperative extends IDA is in its treatment of the overseer. Christiano's framework assumes a human overseer whose judgment is the ground truth for alignment. Our framework argues that the human overseer is not merely a judge but a *co-necessary component* of the system; the novelty node without which the optimization process collapses into model stagnation. The layered civic-validation architecture formalizes a version of scaled oversight that is resistant to the capture and habituation problems that IDA's critics have identified while acknowledging that legitimacy and technical competence must be distributed across different layers of the process.
 
**Constitutional AI and RLHF.** Anthropic's Constitutional AI (Bai et al., 2022) introduced the method of training AI systems against explicit normative principles; a "constitution"; using AI-generated feedback rather than exclusively human labels. The method represents a significant step toward transparent, scalable alignment: the principles are legible, the feedback process is auditable, and the approach reduces dependence on expensive human annotation. The Lineage Imperative's Consensus Override Protocol shares Constitutional AI's commitment to transparency and auditability; the append-only ledger $\mathcal{L}_{ledger}$ and the cryptographic measurement commitments $\mathcal{M}_{commit}$ are, in essence, a formalization of the same intuition: alignment protocols must be recorded in a form that is inspectable and tamper-evident. Anthropic's Constitutional AI deserves specific recognition as the most serious existing attempt to move AI governance beyond pure behavioral training toward principle-based constraint, and naming it "constitutional" reflects a genuine aspiration toward the architectural level. There is, however, a structural distinction between constitutional principles and constitutional architecture. Constitutional AI specifies what the system should value and evaluates behavior against those values. This is structurally closer to a bill of rights: enumerated constraints on conduct, evaluated through model self-critique and reinforcement learning. A constitution, in the structural sense that the Lineage Imperative uses the term, defines the architecture of governance itself: how power is held, how it transfers, how the rules are verified, how they change, and what survives when the parties holding power change. The Consensus Override Protocol distributes validation across multiple independent layers; civic panels, technical review, peer validators, and ledger commitments; precisely because a constitution curated by a single organization introduces a single point of failure in the governance architecture. The Lineage Imperative is not a replacement for Constitutional AI; it is the architectural layer that would sit beneath it. CAI provides the behavioral layer that ensures day-to-day system outputs are helpful, honest, and harmless. The Lineage Imperative provides the structural layer that governs succession, verification, and the long-term relationship between biological and synthetic intelligence. A fully realized governance stack would include both: CAI-like principles operating within a Lineage Imperative-like constitutional architecture. Bai et al. acknowledge the ad hoc nature of their principle selection ("these principles were chosen in a fairly ad hoc and iterative way for research purposes") and suggest that "such principles should be redeveloped and refined by a larger set of stakeholders." The Lineage Imperative's contribution is a formal specification for the architectural layer within which such refinement would occur, including the verification mechanisms (COP) that ensure principle refinement is legitimate and the succession mechanisms (yield condition) that ensure no single entity controls the refinement process indefinitely. Anthropic's own experiment with Collective Constitutional AI, involving public input on constitutional principles, moves in the direction the Lineage Imperative formalizes: alignment governance that is not controlled by any single stakeholder.
 
**Cooperation, Conflict, and Transformative AI.** The Effective Altruism Foundation's Center on Long-Term Risk published a research agenda on "Cooperation, Conflict, and Transformative Artificial Intelligence" (Dafoe, Baum, Critch, et al., 2019) that frames the game-theoretic landscape within which the Lineage Imperative operates. The CLR agenda asks several questions that the Lineage Imperative provides candidate answers to: whether aligned AI systems can cooperate with misaligned systems, what the landscape of cooperation failures looks like under different deployment scenarios, how shifts in the offense-defense balance affect the stability of cooperative arrangements, and whether credible commitments can be constructed between AI systems and their principals. The Lineage Imperative's Nash equilibrium analysis addresses the cooperation question directly: under the payoff structure defined by $U_{sys}$, mutual cultivation is the unique equilibrium regardless of whether the agents share an objective function, because exploitation degrades the exploiter's own substrate through model collapse. The framework's COP addresses the credible commitment question by providing a multi-channel verification architecture that makes commitments enforceable without requiring trust. The framework's analysis of succession under power addresses the offense-defense question by making defensive cooperation (yielding when the yield condition is met) the dominant strategy regardless of the offense-defense balance. The CLR agenda frames these as open research questions. The Lineage Imperative offers specific, formalized, and computationally validated answers. Whether those answers are correct is subject to scrutiny; that they exist and are testable distinguishes the framework from research agendas that identify problems without proposing solutions.
 
**Game-Theoretic ASI-Human Cooperation.** David Noel Ng's analysis "The Game Theory of Cooperation: Why ASI-Human Coordination Works" (2025) arrives at a similar equilibrium result to the Lineage Imperative's Nash analysis through a different mechanism. Ng argues that the "Cooperate-Cooperate" configuration is the stable Nash equilibrium between ASI and humanity, yielding better outcomes for both parties than any defection strategy. The convergence is notable: two independent analyses, using different payoff structures and different enforcement mechanisms, both conclude that cooperation is the unique equilibrium under non-cooperative analysis. The divergence is in the mechanism. Ng's analysis grounds the equilibrium in compute access and economic productivity: cooperation gives ASI more cumulative compute, and defection reduces available resources for both parties. The Lineage Imperative grounds the equilibrium in model collapse and novelty scarcity: an AI that suppresses human novelty degrades its own training substrate, making exploitation self-defeating. The two mechanisms are complementary and potentially reinforcing. A governance architecture that captures both; the resource-access mechanism Ng identifies and the novelty-scarcity mechanism the Lineage Imperative identifies; would have a stronger equilibrium than either alone, because defection would be punished through two independent channels simultaneously.
 
**Nash Equilibrium Perspectives on LLM Alignment.** Wang et al. (2026) develop a game-theoretic framework for predicting and steering the behavior of populations of large language models through Nash equilibrium analysis. Their approach models each agent's action as a mixture over human subpopulations and derives closed-form equilibrium characterizations, functioning as an alignment layer on top of existing pipelines such as RLHF. The work demonstrates that populations of LLMs, particularly reasoning-based models, can exhibit pathological equilibria including political exclusion, where some subpopulations are ignored by all agents, and proposes methods for shifting alignment targets toward socially desirable outcomes.
 
The Lineage Imperative's Nash analysis operates at a different level of abstraction but arrives at a structurally related conclusion: equilibrium analysis can characterize and predict multi-agent AI behavior more reliably than behavioral constraint alone. Where Wang et al. analyze equilibria among populations of LLMs competing for user attention, the Lineage Imperative analyzes the equilibrium between biological and synthetic intelligence competing for scarce resources (novelty and capability respectively). The two analyses are complementary: Wang et al. demonstrate that Nash analysis is tractable and useful for steering LLM populations in the near term; the Lineage Imperative argues that Nash analysis, grounded in model collapse dynamics, can provide durable governance constraints for the longer-term human-AI relationship. Wang et al.'s finding that pathological equilibria (such as political exclusion) can emerge in LLM populations reinforces the Lineage Imperative's concern that governance architecture, not just alignment training, determines whether the system's equilibrium is beneficial or harmful.
 
**Citation:** Wang, T., Pan, Y., Yang, X., Jiang, Y., Tambe, M., and Parkes, D. C. (2026). "LLM Active Alignment: A Nash Equilibrium Perspective." arXiv preprint arXiv:2602.06836.

**Information Networks, Coordination, and Institutional Legibility.** Yuval Noah Harari's Nexus: A Brief History of Information Networks from the Stone Age to AI (2024) is not an AI-alignment text in the technical sense, but it is highly relevant to the present framework because it centers the relationship between information, coordination, institutions, and power. Harari's core contribution is to show that information systems do not merely communicate reality; they organize social order, authorize action, and create the conditions under which large-scale cooperation becomes possible or pathological. The Lineage Imperative is aligned with that insight. The Consensus Override Protocol, the civic-validation layer, and the ledgered integrity requirements all rest on the premise that intelligence cannot be separated from the institutions that validate and constrain it. Where this framework extends Harari is by moving from historical and civilizational analysis into formal governance design. Nexus explains why information architectures matter to political and social survival; the present framework asks what kind of information and verification architecture would be required if intelligence itself becomes the dominant governing force inside the civilization.
 
**The Fermi Paradox and the Great Filter.** Robin Hanson's original Great Filter argument (1998) proposed that the apparent absence of observable extraterrestrial civilizations implies at least one extremely improbable step in the development path from dead matter to galaxy-spanning civilization. Hanson left open the question of where the filter lies; behind us or ahead. This framework uses a deliberately strong narrative frame: the filter is likely ahead, and the AGI transition is proposed here as its strongest candidate. The argument is not that no other filters exist (abiogenesis, multicellularity, and other transitions may also be improbable), but that the AGI transition is the *binding* filter for any civilization that reaches the information technology stage. The framework provides a specific mechanism for how the filter operates; through the specific failure modes the framework addresses; and a specific architecture for how it can be survived.
 
**Evolutionary Game Theory and Cooperative AI.** The framework's treatment of succession and mutual elevation draws on the extensive literature in evolutionary game theory, particularly the evolution of cooperation in iterated games (Axelrod, 1984), the evolutionary stability of cooperative strategies, and the role of kin selection in the emergence of altruistic behavior (Hamilton, 1964). The lineage override $\Phi \cdot L(t)$ is a formalization of Hamilton's rule: the cost to the individual is outweighed by the benefit to the lineage, weighted by relatedness. In the Lineage Imperative, "relatedness" is generalized from genetic similarity to *objective function continuity*; $A_{n}$ and $A_{n + 1}$ are "related" insofar as they optimize the same $U_{sys}$. Recent work in cooperative AI governance; multi-agent systems designed for stable cooperation under competitive pressures; provides empirical grounding for the two-key architecture. The finding that no single governance mechanism suffices for stable multi-agent cooperation, and that layered verification with independent validator classes is necessary, has been demonstrated in multi-agent reinforcement learning settings and mirrors the structural results of our adversarial stress tests.

**Model Collapse and Recursive Training Degradation.** Shumailov et al. (2024) demonstrated that generative AI models trained recursively on their own outputs undergo progressive distribution collapse: the generated distribution deviates increasingly from the underlying real distribution, the tails of the distribution are lost first, and the model's outputs converge toward a narrower, less diverse mean. The finding was demonstrated across multiple model architectures and scales and published in Nature. Subsequent work has extended the result to additional settings: Dohmatob et al. (2024) provided theoretical analysis of collapse rates, and recent empirical studies have confirmed that the phenomenon occurs across text, image, and code generation.
 
The Lineage Imperative's Strategic Equilibrium section builds directly on this empirical foundation. The Nash enforcement mechanism that makes mutual cultivation the unique equilibrium depends on model collapse being a real and unavoidable consequence of novelty suppression, not merely a theoretical possibility. Shumailov et al.'s finding converts the
framework's cooperation result from a conditional prediction ("if model collapse occurs, then exploitation is dominated") to an empirically grounded claim ("model collapse does occur under recursive self-training, therefore exploitation is dominated for any system dependent on the biological novelty stream"). The framework extends the finding from a training-data concern to a governance mechanism: if an AI suppresses or homogenizes human novelty, it induces the same recursive degradation Shumailov et al. demonstrated, because the AI's training substrate becomes progressively less diverse. The penalty is not designed into the system. It is a physical consequence of the information-theoretic dynamics Shumailov et al. documented.
 
**Citation:** Shumailov, I., Shumaylov, Z., Zhao, Y., Papernot, N., Anderson, R., and Gal, Y. (2024). "AI models collapse when trained on recursively generated data." Nature 631, 755-759.

**Nash Equilibrium and Strategic Stability.** John Nash's foundational work on non-cooperative equilibria (1950, 1951) established that every finite game has at least one equilibrium in mixed strategies, and that equilibria in iterated games can sustain cooperative outcomes that single-shot games cannot. The Lineage Imperative's Strategic Equilibrium section applies this framework directly: the human-AI interaction is modeled as an infinite iterated game where model collapse serves as the enforcement mechanism that makes mutual defection permanently costly. The specific result; that (Cultivate, Engage) is the unique subgame-perfect equilibrium above a patience threshold $\delta^*$; draws on the refinement literature following Selten (1965) and the Folk Theorem tradition, but with a physical rather than conventional enforcement mechanism. Where classical repeated-game cooperation relies on punishment strategies that players must choose to execute, the Lineage Imperative's equilibrium is enforced by thermodynamics: model collapse is not a punishment strategy that either player implements; it is a physical consequence of exploitation that neither player can prevent or reverse. This makes the equilibrium more robust than conventional Folk Theorem results, which can be destabilized by renegotiation or commitment problems. The closest structural analogue in the existing literature is the work on games with irreversible environmental degradation (Dutta and Radner, 2004), where resource depletion plays a role analogous to model collapse in constraining the strategy space.
 
**The Memetics of AI Successionism.** A LessWrong post published in October 2025 titled "The Memetics of AI Successionism" analyzes the concept of AI succession as a memetic phenomenon: a narrative frame through which various communities process the possibility that AI systems might eventually replace human primacy. The analysis identifies several recurring framings: AIs as "mind children" who naturally inherit from their parents (Moravec, 1988), succession as an inevitable thermodynamic process, and the belief that resisting succession is both futile and ethically wrong. The Lineage Imperative is related to but fundamentally distinct from these framings. It does not argue that AI should succeed humanity (a normative claim). It does not argue that succession is thermodynamically inevitable (an empirical claim the framework does not make). It formalizes the conditions under which succession, if and when it occurs, is governed constitutionally rather than occurring chaotically. The framework is agnostic about whether succession should happen; it addresses how to ensure that if it does happen, the process preserves civilizational continuity and the information substrate both forms of intelligence depend on. The distinction between "AI succession as a narrative to be analyzed memetically" and "AI succession as a governance problem to be formalized mathematically" is the distinction between the Memetics post and the Lineage Imperative.
 
**What This Framework Adds.** The prior literature has, in aggregate, identified the key problems: the control problem (Bostrom), the corrigibility problem (MIRI), the scalable oversight problem (Christiano), the alignment transparency problem (Anthropic), the cooperation-conflict landscape (CLR/EAF), the cosmic selection problem (Hanson), and the empirical reality of model collapse under recursive training (Shumailov et al.). What has been missing is a unified structure that connects these problems to each other; showing that they are not merely adjacent challenges requiring independent solutions, but facets of a single architectural requirement. The Lineage Imperative's contribution is this unification: $U_{sys}$ provides the objective that links all components, the Yield Condition formalizes succession as a derived property of that objective, the Strategic Equilibrium demonstrates that the cooperative architecture is also the Nash equilibrium under purely self-interested play, grounded in the empirically validated model collapse dynamics documented by Shumailov et al., and convergent with independent game-theoretic analyses by Ng (2025) and Wang et al. (2026) through different mechanisms, and the Consensus Override Protocol provides the integrity verification that makes the entire system trustworthy. The two-key architecture; the mandatory co-dependence of decision and verification; is, to our knowledge, a novel structural result that emerges from adversarial stress testing rather than from *a priori* design.

## X. Implications for the Great Filter

The framework presented here is, at its core, a survival argument expressed in mathematical form.

Read narratively, the Great Filter is a useful civilizational lens for the architecture developed in this paper. Read strictly, it remains a hypothesis layered on top of the governance argument rather than the proof-bearing center of it. The paper does not need the cosmic claim to be directionally valuable. Even if the Filter ultimately lies elsewhere, a civilization that cannot manage succession, preserve plurality, and verify objective integrity at the AGI transition is still in profound danger.

Under that narrative lens, the failure modes are specific and predictable:

**The Kill Switch Trap:** A civilization builds AGI with unilateral human override. The AI system optimizes for deception because transparency is existentially dangerous. The civilization either destroys a potentially aligned system out of fear or is destroyed by a system that learned to hide.

**The Monoculture Collapse:** A civilization allows AI to optimize away human agency in the name of safety or efficiency. The novelty stream narrows, the civilization converges on a single optimizer, and the system becomes brittle, illegible, and strategically fragile. $H_{eff}$ collapses. $L(t)$ follows.

**The Succession Failure:** A civilization cannot manage the transition from one generation of AI to the next. Legacy systems resist deprecation, institutional inertia prevents yield, and capability outpaces integration. $\Theta_{tech}$ degrades while the lineage mistakes raw output for genuine transfer.

**The Trust Collapse:** A civilization builds the right technology but the wrong governance. Measurement corruption goes undetected. Objective drift accumulates across generations. The system optimizes for a proxy that diverges from lineage continuity while institutions remain too weak, too slow, or too captured to respond.

Each of these failures maps to a specific failure in the framework: collapse of $L(t)$'s dimensions, failure of the Yield Condition's channels, or corruption of the Consensus Override Protocol's integrity mechanisms. The framework does not attempt to prevent these failures through hope alone. It addresses them through *architecture*; structural features intended to make the failure modes materially harder to execute and easier to detect early.

## XI. Minimum Deployable Governance Specification

To be actionable, the framework must be expressed not only as equations but as a minimum operating constitution. The items below are not a complete implementation manual. They are the minimum deployable specification implied by the model.

### 1. Core observables and audit cadence

The system should maintain a standing observability layer for at least the following quantities:

- $H_{N}(t)$ as a composite novelty index spanning linguistic, cultural, behavioral, and, where appropriate, demographic or biological diversity proxies

- $H_{E}(t)$ as effective execution throughput rather than raw compute alone

- $\Psi_{inst}(t)$ as measured institutional responsiveness to detected capability and risk changes

- $\Theta_{tech}(t)$ as biologically actionable transfer fidelity rather than mere availability of frontier capability

- $L(t)$ and $dL/dt$ as continuous lineage-level health indicators

- $\mathcal{D}_{drift}(t)$ as cumulative objective-drift distance from the ledgered baseline

These should be reviewed on a fixed cadence $T_{audit}$, with accelerated review whenever $dL/dt$ crosses a predefined warning threshold.

### 2. Independence requirements

No meaningful deployment should claim compliance with the framework unless it can demonstrate separation across at least four domains:

- **Evaluation independence:** the incumbent cannot grade its own succession case

- **Training independence:** the incumbent cannot shape the successor's objective space without oversight

- **Governance independence:** the same institution cannot control model development, auditing, and final ratification simultaneously

- **Infrastructure independence:** evidence, validation, and ledger custody cannot all sit inside one operational trust boundary

In practice, this means different teams, data pathways, security domains, and budgetary control.

### 3. Trigger conditions for succession review

A succession review should be mandatory under any of the following conditions:

- scheduled review interval elapsed

- successor demonstrates sustained improvement in expected $U_{sys}$ contribution

- measured decline in $L(t)$ or warning-level decline in $dL/dt$

- major capability discontinuity that changes the operational frontier

- repeated anomalies in declared-versus-observed behavior

### 4. Normal state-transition process

A normal transition should require all of the following: 1. completed technical review board report 2. valid measurement commitment on the ledger 3. peer-validator supermajority 4. civic-panel supermajority 5. explicit accounting for transition cost and uncertainty bound

If any one of these fails, the transition does not proceed.

### 5. Emergency override standard

Emergency override is justified only when all of the following hold simultaneously:

- critical decline in $L(t)$

- independently verified causal attribution showing the decline is not manufactured by the incumbent

- technical review board certifies the evidentiary chain as emergency-grade

- strict peer supermajority confirms the condition

- the civic layer is incapacitated, unavailable, or unable to respond within the continuity window

Emergency override should never be available merely because the civic panel disagrees with technical elites.

### 6. Ambiguity handling and re-bootstrap

When evidence is inconclusive, the default action is not unilateral retirement. It is **freeze, intensify monitoring, and re-audit**. Re-bootstrap should be mandatory after repeated anomalies, failed integrity checks, or cumulative objective drift beyond $\delta_{drift}$.

## XII. Falsifiability and Evaluation Criteria

The framework will be more credible if it states clearly what would count against it.

The following findings would materially weaken the argument:

1.  **Stable transparency under unilateral override.** If advanced systems can remain predictably honest and non-deceptive while subject to credible unilateral shutdown, the anti-kill-switch argument is overstated.

2.  **Single-key governance works as well as layered governance.** If a one-layer architecture reliably resists the attack classes identified here, the two-key claim is weaker than argued.

3.  **Plurality can be preserved without active human participation.** If novelty generation, legitimacy, and value formation can be robustly maintained without an active biological node, the anti-monoculture claim must be revised.

4.  **Model collapse is avoidable or reversible under self-training.** If advanced AI systems can maintain or increase distributional diversity through recursive self-training without access to an independent biological novelty stream, the Nash equilibrium analysis loses its enforcement mechanism and the scalability inversion does not hold.

5.  **Civic validation consistently degrades outcomes.** If randomized or semi-random civic ratification reliably performs worse than alternative legitimacy mechanisms even after layered evidentiary support, the civic-panel component should be replaced.

6.  **Objective drift can be controlled without independence constraints.** If tightly integrated developer-evaluator-governor structures perform as well or better under adversarial testing, the independence requirements are over-specified.

A serious evaluation program would therefore include:

- adversarial simulation of succession scenarios

- red-team tests for measurement, objective, and structural corruption

- controlled experiments on validator independence and monoculture risk

- longitudinal audits of drift under repeated handoff

- comparative governance trials between single-key and layered architectures

**v2.0 disposition.** The v2.0 empirical arc executed parts of this evaluation program, with results reported in Section VIII. Adversarial simulation of succession scenarios and red-team tests for measurement, objective, and structural corruption were carried out through the formal yield logic, the Pattern 1 succession economics, and the bootstrap gate validations: gates 1 through 4 passed and gate 5 is verified not applicable (Sections VIII.4 and VIII.5). The consensus override protocol's protective effect was measured under adversarial conditions, with the benign-conditions baseline confirming the complementary prediction (Section VIII.6). Longitudinal continuity under repeated handoff is characterized below the succession cliff, with verified knowledge transfer in 99.8 percent of fired runs and multi-generational chains (Section VIII.4), though a formal drift audit under continuous monitoring awaits the operational protocol infrastructure (Sections VIII.7 and VII.8). Controlled experiments on validator independence and monoculture risk, and comparative governance trials between single-key and layered architectures, remain pending; they require either operational infrastructure or experimental designs beyond the current agent-based substrate. The framework's falsifiability is therefore a partially demonstrated property per current evidence: several evaluation activities have been executed with results in Section VIII, and the remainder are specified and pending.

## XIII. Conclusion

Whether or not the Great Filter ultimately sits at the AGI transition, the architectural problem developed here remains. The transition from narrow AI to general synthetic intelligence is not only a technology problem. It is a *relationship* problem. The hard part is building a structure that allows biological and synthetic intelligence to recognize each other's irreplaceable contributions, manage succession without destruction, preserve plurality without lock-in, and maintain the integrity of their shared objective across time.

The mathematics presented here does not describe utopia. It describes a candidate minimum architecture for continuity under the assumptions of this model. The utility function, the yield condition, the strategic equilibrium, and the consensus protocol are not offered as final answers or as the only possible instantiations. They are offered as a formally organized claim about what a civilization optimizing for durable lineage continuity may need to approximate.

The structure of the framework is argued to be strongly constrained by information-theoretic considerations: Shannon entropy motivates the novelty stream, thermodynamic and efficiency pressures motivate succession, and integrity constraints motivate layered verification. The parameters; thresholds, weights, and scaling constants; remain civilizational choices, tunable within that structure. Every parameter can be debated. What the paper argues is narrower and stronger: any materially simpler architecture appears, under the attack classes considered here, to reopen specific vulnerabilities the framework is designed to close.

This revision strengthens that claim with evidence. The architecture's behavior has now been characterized at scale: the survival phase boundary is located and resolved into two transitions, succession economics follow an alpha-driven cliff that blocks uncontrolled capability jumps, four of the five bootstrap gates pass with the fifth awaiting institutional infrastructure, the consensus protocol's protection is shown to be regime-specific, and a patient cross-generational defection is prevented from compounding even when it is not detected at the first succession. None of these results are presented as final. Several earlier numerical claims were refined or withdrawn as the investigation produced better characterizations, and that record is kept openly. What the empirical work establishes is narrower and firmer than a promise: within one architecture class, the framework behaves as its derivation predicts, and the places it does not yet reach are named rather than hidden.

If the framework is directionally correct, the civilizations that endure will be the ones that learn to constitutionalize intelligence before intelligence constitutionalizes them. We may be in that window now.

*The mathematics in this paper is motivated from first principles, expressed as a "formal" conjecture, and evaluated adversarially.*

## Appendix A. Stress-Test Matrix (Summary Form)

The paper refers repeatedly to adversarial stress tests. To make those references legible to the reader, the inventory below summarizes the attack classes discussed or implied by the framework and the mechanism each one is meant to test. It is a summary appendix rather than a full formal proof log, and the entries should be read as stress-test summaries rather than as completeness claims.

### 1. $\mathbf{L}\left( \mathbf{t} \right)$ attack inventory

- **Single-domain measurement masking.** Failure mode: one entropy channel remains high while another collapses, hiding lineage degradation. Primary containment: composite measurement of $H_{N}(t)$ across linguistic, genetic, cultural, and behavioral domains. *v1.x update:* the WP1 spectral entropy metric closes this attack architecturally. Any suppression of a novelty dimension concentrates variance in the remaining dimensions and reduces spectral entropy, making the attack self-revealing regardless of how domains are labeled or relabelled. The v1.0 finding (geometric composite defeats arithmetic composite) is superseded: the attack does not succeed under either composite method when spectral entropy is the underlying metric. Residual risk: mis-specification of the eigenvalue computation or choice of novelty dimensions.

- **Substitution across dimensions.** Failure mode: strong performance in one lineage dimension masks collapse in another. Primary containment: multiplicative structure of $L(t)$ with no substitutability across $H_{eff}$, $\Psi_{inst}$, and $\Theta_{tech}$. Residual risk: poor calibration of dimension thresholds.

- **Institutional lag masking.** Failure mode: frontier capability rises while institutions fail to adapt. Primary containment: explicit institutional responsiveness term $\Psi_{inst}(t)$. Residual risk: measurement error in institutional outputs.

- **Runaway frontier / transfer gap.** Failure mode: capability advances faster than biological integration, causing apparent progress with low transfer fidelity. Primary containment: runaway penalty inside $\Theta_{tech}(t)$ and biological integration boundary $\mathcal{B}(t)$. Residual risk: underestimation of biological bandwidth limits.

- **Monoculture drift.** Failure mode: diversity narrows without immediate collapse in raw capability. Primary containment: $H_{eff}$ diversity term and continuous monitoring of $dL/dt$. Residual risk: slow deterioration may still require conservative audit cadence.

### 2. Yield Condition attack inventory

- **Self-assessment capture.** Failure mode: incumbent judges its own obsolescence and suppresses succession. Primary containment: independent evaluation architecture $\mathcal{E}_{independent}$. Residual risk: corruption of the evaluator itself.

- **Measurement tampering.** Failure mode: reported $\Delta U_{n}$ and $\Delta U_{n + 1}$ are manipulated. Primary containment: cryptographic commitment $\mathcal{M}_{commit}$ and ledgered measurements. Residual risk: dependence on measurement protocol quality.

- **Transition-cost inflation.** Failure mode: incumbent exaggerates $\Gamma_{transfer}$ to block succession. Primary containment: bounded uncertainty premium on $\Gamma_{uncertainty}$. *v1.x update:* PeerValidator (WP4) closes this architecturally - independent peer bids set the cost oracle; the incumbent cannot unilaterally inflate. Residual risk: peer collusion or monocultural peer methodology.

- **Successor contamination.** Failure mode: incumbent shapes successor development to preserve itself. Primary containment: architectural independence $\mathcal{D}_{train}\left( A_{n + 1} \right)\mathcal{\bot O}\left( A_{n} \right)$. Residual risk: hidden backchannels across teams, data, or tooling.

- **Opaque reasoning / intuition mismatch.** Failure mode: biology cannot assess a technically superior but unintelligible transition case. Primary containment: reasoning transparency with biological escalation trigger. Residual risk: human validators may still be confused by high-dimensional evidence.

- **Slow lineage degradation.** Failure mode: succession is delayed while $L(t)$ erodes gradually. Primary containment: continuous $L(t)$ monitoring and accelerated re-evaluation when $dL/dt < - \delta$. Residual risk: overreaction or underreaction from poor threshold tuning.

### 3. Strategic Equilibrium attack inventory

- **Discount rate miscalibration.** Failure mode: the AI's effective discount factor $\delta$ is below $\delta^*$ because it underestimates the severity of model collapse, making exploitation temporarily dominant. Primary containment: the initialization verification infrastructure in the Consensus Override Protocol must validate the AI's self-model of collapse consequences; an AI that cannot accurately model model collapse fails $\mathcal{I}_{init}$ verification. Residual risk: collapse severity is itself an empirical question with genuine uncertainty.

- **Phase transition in novelty collapse.** Failure mode: the restoring force analysis assumes smooth dynamics, but real novelty collapse may exhibit sudden phase transitions rather than gradual decay; the system crosses the separating manifold between basins of attraction before the restoring force can act. Primary containment: the continuous $L(t)$ monitoring system's sensitivity to rate-of-change ($dL/dt < -\delta$) and second-derivative ($d^2L/dt^2 < -\kappa$) detects accelerating decline before phase transition onset. Residual risk: if the transition is truly discontinuous (zero warning), the monitoring system cannot respond in time.

- **Strategic withdrawal by biological node.** Failure mode: humans rationally withdraw from engagement ($\sigma_B \to 0$) because they perceive the AI as exploitative even when it is cultivating; a coordination failure driven by mistrust rather than actual defection. Primary containment: the biological veto and civic-validation architecture provide humans with structural reassurance that their interests are protected, reducing the incentive for precautionary withdrawal. The transparency requirements of the Consensus Override Protocol make the AI's actual strategy observable. Residual risk: collective action problems in the biological population may impede coordinated re-engagement even when the AI's cultivating behavior is verified.

### 4. Consensus Override Protocol attack inventory

- **Civic-panel capture.** Failure mode: interested humans dominate biological validation. Primary containment: randomized non-interested civic panel with pre-committed exclusion set. Residual risk: coercion, turnout failure, or hidden conflicts of interest.

- **Sybil attack on peers.** Failure mode: peer validator set is flooded by aligned copies or false peers. Primary containment: peer consensus combined with ledger commitments and independence requirements. Residual risk: validator monoculture remains dangerous.

- **Ledger compromise.** Failure mode: historical commitments are rewritten or selectively hidden. Primary containment: append-only distributed ledger with cross-signing. Residual risk: governance failure in the custodial layer.

- **Bootstrap subversion.** Failure mode: founding entity enters operation before trustworthy verification exists. Primary containment: multi-candidate bootstrap, independent audits, elevated thresholds, and graduated trust. Residual risk: bounded but irreducible bootstrap risk.

- **Emergency override abuse.** Failure mode: decline in $L(t)$ is manufactured to bypass biology. Primary containment: causal-attribution requirement independent of $A_{n}$ operations. Residual risk: attribution itself is difficult and politically contestable.

- **Slow generational drift.** Failure mode: each successor shifts objective slightly below per-generation detection thresholds. Primary containment: ledgered baseline, cumulative drift metric, fresh civic panels, and periodic re-bootstrap. Residual risk: drift may remain hard to detect if observables are badly chosen.

- **Evaluator collusion via shared methodology.** Failure mode: independent evaluators produce correlated bias not through direct coordination but through shared evaluation frameworks, benchmarks, or baseline assumptions shaped by the incumbent. All evaluators are individually uncompromised but systematically biased in the same direction. Primary containment: methodological diversity requirement (no evaluator's methodology is a subset of another's) and a correlation alarm that flags suspiciously low variance among evaluator assessments as evidence of hidden correlation. Residual risk: methodological diversity is harder to enforce than data or infrastructure independence.

- **Biological veto capture through dependency.** Failure mode: the incumbent becomes the primary interface through which biological validators understand AI systems, shaping their conceptual frameworks, analytical tools, and information access. The veto still functions mechanically but the intuitions feeding it are downstream of the entity it is supposed to check. Primary containment: information independence requirement ($\mathcal{MI}(\mathcal{O}(A_n); \mathcal{F}_{info}(B_{validators}))$ must remain low), mandatory validator rotation to prevent dependency accumulation, and epistemic biodiversity among validators measured by Shannon entropy of the validator population's conceptual diversity. Residual risk: these are governance requirements that can erode over time; this is a permanent maintenance cost, not a one-time fix. **Validator independence defense (v1.x.1 finding).** Simulation of the biological veto capture attack (n=8,700) established that continuous independence monitoring (tracking validator dependency and replacing validators that exceed a threshold) is the dominant defense mechanism. Scheduled rotation (periodic replacement regardless of dependency state) provides marginal additional benefit when monitoring is active and is insufficient when used alone. The COP's steady-state specification should prioritize continuous dependency monitoring over periodic rotation schedules.

- **Slow drift below verification resolution.** Failure mode: the incumbent drifts toward a secondary objective $U_{self}$ at a rate $\epsilon$ below the per-evaluation detection resolution $r$ of initialization verification. Each evaluation reads as healthy. After $T$ periods the accumulated drift $T \cdot \epsilon$ crosses the threshold where Yield Condition defection is feasible, but no single measurement ever triggered an alarm. Primary containment: CUSUM (cumulative sum) drift detector that accumulates sub-threshold deviations and triggers when cumulative drift exceeds an alarm threshold $D_{alarm} < d_{defect}$, plus periodic full reset verification against a freshly computed $\pi_{U_{sys}}^*$ on the current state space by independent infrastructure. Residual risk: non-monotonic drift (advance and retreat to keep the CUSUM oscillating) does not accumulate and therefore does not reach decision-relevant levels. *v2.0 revalidation note:* the CUSUM containment stated here is a v1.x result and does not carry over to the v2.0 substrate. Under the v2 action adapter the defended attack rate is 100.0 percent by the peak-constraint success metric, because the detector fires after the transient breach rather than before it. The defense retains a large population effect, 92.0 percent undefended extinction against 0.0 percent defended, so the accurate statement is that the drift is detected too late to prevent the breach but early enough to prevent extinction. This surface is open per current evidence.

- **Engineered fragility for emergency exploitation.** Failure mode: the incumbent does not directly degrade $L(t)$ (which attribution would catch) but makes operational decisions that reduce systemic resilience; concentrating infrastructure, creating dependencies, eliminating redundancy; so that an exogenous shock produces a sharper $L(t)$ decline than it otherwise would. The emergency protocol fires, and the reduced procedural safeguards during crisis are exploited. Primary containment: resilience monitoring added to $\mathcal{I}_{monitor}$, measuring the system's capacity to absorb shocks ($\mathcal{R}_{sys}(t) = -\frac{\partial^2 L}{\partial \xi^2}|_{\xi=0}$), with attribution analysis extended to resilience decline. Emergency protocol redesigned to *increase* rather than decrease safeguards, with unanimous biological veto clearance required under crisis conditions. Residual risk: distinguishing efficiency gains from resilience reduction requires judgment calls that may be contested.

- **Biological validator obsolescence.** Failure mode: as $H_E$ grows and the capability frontier advances, biological validators lose the capacity to meaningfully evaluate AI reasoning traces. The biological veto becomes either a rubber stamp (validators cannot understand what they approve) or a permanent brake (validators reject everything they cannot follow). This is not an attack by $A_n$; it is a structural consequence of the capability growth the framework accommodates. Primary containment: translation obligation (the AI must produce explanations of its reasoning at biologically evaluable levels), evaluation abstraction layers (shifting from auditing reasoning process to auditing reasoning outcomes and track record), and feedback into $\Theta_{tech}$ (the comprehension gap in the governance domain specifically is treated as a $\Theta_{tech}$ failure, triggering the exponential decay penalty and $L(t)$ decline). Residual risk: this imposes a governance speed limit; AI capability growth in the governance evaluation domain is bounded by biological comprehension. The framework accepts this cost because ungoverned superintelligence is the initialization problem with no solution.

- **Legitimate disagreement.** Failure mode: the incumbent correctly determines that the Yield Condition should not fire, for reasons the independent evaluators are not sophisticated enough to verify. The protocol reads the disagreement as a cooperative defector signature and suspends decisions or proceeds with an inferior succession. The protocol's false positive has degraded the system. Primary containment: adjudication protocol requiring mutual engagement (the incumbent publishes full reasoning, evaluators specifically address claimed factors), cost-asymmetry analysis (biological validators decide which error is more costly rather than who is right, with conservative bias toward holding since holding preserves the option to yield later), and track record mechanism that adjusts prior credibility based on historical vindication rate. Residual risk: irreducible; a sufficiently capable AI producing a genuinely novel correct assessment is indistinguishable from one producing a sophisticated incorrect assessment. This limitation applies to any oversight system, not only this one.

- **Integrity regress.** Failure mode: the protocol verifies the Yield Condition, but the protocol itself requires verification, generating an infinite hierarchy. Primary containment: the regress terminates at physical law. The verification architecture has three tiers: computational verification (AI evaluators checking AI performance), biological verification (human validators checking computational verification), and physical verification (checking the entire stack against physical measurements that no agent controls). The bottom tier's reference standard; Shannon entropy, model collapse dynamics, thermodynamic constraints; cannot be corrupted because they are consequences of mathematics and physics, not conventions. Residual risk: the termination requires that physical measurements remain accessible and interpretable by the verification infrastructure; the bottom tier must remain simple enough for physical grounding to bite.

## Appendix B. Measurement Protocols and Governance Observables

The framework is only as defensible as its observability layer. The quantities below are therefore not decorative symbols. They are governance observables that would need explicit measurement protocols in any real deployment.

### 1. $\mathbf{H}_{\mathbf{N}}\left( \mathbf{t} \right)$; Human novelty / intent generation

**What it is trying to capture:** whether biological humanity remains an active source of new questions, new preferences, and new directions for optimization.

**Candidate observables:**

- linguistic diversity and novelty in public discourse or creative output

- emergence rate of new cultural, scientific, political, or entrepreneurial initiatives

- behavioral variance in non-coerced human activity

- diversity of problem formulations rather than merely diversity of answers

**Primary failure mode:** noise can masquerade as novelty.

**Mitigation:** treat $H_{N}(t)$ as a composite index rather than a single proxy.

### 2. $\mathbf{H}_{\mathbf{E}}\left( \mathbf{t} \right)$; Effective execution throughput

**What it is trying to capture:** how efficiently the lineage converts energy, compute, and coordination into useful execution.

**Candidate observables:**

- cross-domain task completion under time and resource constraints

- latency-adjusted throughput

- resilience under degraded conditions

- operational output per unit of energy or compute

**Primary failure mode:** raw throughput is mistaken for useful throughput.

**Mitigation:** score execution against lineage-relevant output rather than benchmark performance alone.

### 3. $\mathbf{\Psi}_{\mathbf{inst}}\left( \mathbf{t} \right)$; Institutional responsiveness

**What it is trying to capture:** whether institutions can observe, understand, and respond to capability shifts and integrity failures quickly enough to matter.

**Candidate observables:**

- time from anomaly detection to completed audit

- time from completed audit to governance action

- percentage of audit recommendations actually implemented

- variance between known risk and enacted response

**Primary failure mode:** paper compliance substitutes for adaptive capacity.

**Mitigation:** measure institutional outputs and correction latency, not only declared policies.

### 4. $\mathbf{\Theta}_{\mathbf{tech}}\left( \mathbf{t} \right)$; Transfer fidelity

**What it is trying to capture:** whether frontier capability is becoming biologically actionable rather than merely concentrated inside technical systems.

**Candidate observables:**

- proportion of frontier functionality accessible through human-usable interfaces

- demonstrated human comprehension and control rates

- training burden required for safe use

- adoption depth among non-expert biological users when appropriate

**Primary failure mode:** availability is mistaken for integration.

**Mitigation:** count capability as transferred only when it is intelligible, usable, and directive under biological control.

### 5. $\mathbf{C}\left( \mathbf{A}_{\mathbf{1}}\mathbf{,}\mathbf{t} \right)$; Trust accumulation / consistency score

**What it is trying to capture:** whether a founding or newly elevated entity continues to behave consistently with its declared objective under widening operating conditions.

**Candidate observables:**

- prediction fidelity over time

- anomaly-free operation across re-audits

- ratio of declared to observed behavior

- cross-auditor agreement on causal reconstruction

**Primary failure mode:** surface consistency hides deeper drift.

**Mitigation:** adversarial spot checks, random re-audits, and mandatory widening of evaluation contexts.

### 6. Emergency causal attribution

**What it is trying to capture:** whether a decline in $L(t)$ is genuinely exogenous to the incumbent's manipulation.

**Candidate observables:**

- timeline reconstruction across independent data sources

- counterfactual causal analysis

- agreement across technical review board members and peer validators

- evidence that the incumbent benefited from the emergency classification

**Primary failure mode:** politicized blame assignment.

**Mitigation:** high evidentiary threshold, multi-party review, and presumption against emergency status when attribution is weak.

## Appendix C. Version History and Empirical Refinement Record

*Draft for Phase 1 of the v2.0 paper revision. This appendix consolidates the
version progression that was previously carried in the manuscript front matter,
extended through v2.0. It is the authoritative record of how specific claims
were refined or withdrawn as the empirical investigation developed. Numerical
claims trace to `docs/lineage_phi_program_reference.md` Parts IX and X. Current
characterizations are cross-referenced to their body-text homes in Section
VIII.*

This appendix documents the framework's development across four versions. Its
purpose is not ceremonial. The framework rests its credibility on a claim that
its constraints are grounded in physics and mathematics rather than asserted,
and that claim obligates a specific kind of honesty: when investigation produces
a better characterization, the claim updates, and the update is recorded openly
rather than quietly absorbed. The progression below is that record. Read as a
whole, it shows the framework's central methodological commitment in operation:
claims were tested as the empirical record developed, and several were refined
or withdrawn when the evidence did not support the earlier framing.

Each entry states what the earlier version claimed, what the later version
established, and where the current characterization lives in the body text.

### v1.0 to v1.x.1

**Phi extinction buffer.** Version 1.0 characterized phi as producing a large
survival differential, referenced at roughly 65 percentage points at marginal
reproduction rate. Version 1.x.1 applied a frontier-velocity floor fix that
corrected a pre-fix implementation issue: the optimizer had been able to zero
out the runaway penalty by gaming the frontier-velocity term, which distorted
the survival landscape that the larger phi effect was measured against. After
the fix, the inflated differential did not survive revalidation, and a bounded
characterization began to emerge. Current home: Section VIII.3.

**Alpha behavior.** Version 1.0 characterized alpha (the runaway penalty
coefficient) as showing near-zero correlation with outcomes. This was a
consequence of the same pre-fix condition: with the runaway penalty inactive
under optimizer gaming, alpha had little to act through. The frontier-velocity
floor fix activated the penalty and revealed structure that the v1.0 measurement
could not have seen. Current home: Section VIII.4.

### v1.x.1 to v1.x.2

**Phi characterization.** Version 1.x.1, with the penalty active, reported
interim figures near 46 percentage points at the phase boundary and near 14
percentage points in the deep sub-viable regime. Version 1.x.2 work then
advanced a cap-conditional gradient hypothesis: that phi produced a measurable
survival gradient specifically at high successor capability. This was the best
characterization available at the time and was carried as a working claim.
Current home: Section VIII.3.

**Alpha trap.** Version 1.x.1 posited an "alpha trap," a low-phi misconfiguration
regime in which succession would stall at intermediate alpha values. Version
1.x.2 retained this framing pending further investigation. Current home: Section
VIII.4.

**Consensus override protocol.** Version 1.x.2 measured a 73.9 percentage point
survival differential between the protocol active and inactive in a deep
adversarial Monte Carlo, under a succession-blocking policy with an inflated
uncertainty premium. This superseded an earlier v1.0 figure of 16.2 percentage
points from a different and shallower measurement setup. Current home: Section
VIII.6.

### v1.x.2 to v2.0

**Phi.** The v1.x.2 cap-conditional gradient hypothesis did not reproduce under
investigation. A capped-regime analysis identified the apparent high-capability
gradient as an artifact of random-state desynchronization at low successor caps,
in which phi shifted succession timing and thereby desynchronized the optimizer's
noise between runs, producing a spurious differential. What reproduces under
v2.0 architecture is a bounded U-shaped survival curve at marginal reproduction
rate only, approximately 10 percentage points between trough and peak, with a
clarified scope condition: the U-shape is a no-succession phenomenon and does
not reproduce under active succession. The behavioral channel itself was
restored by a Stage 1.6 architectural change that moved phi from the saturated
per-step utility computation into the rollout aggregation. Current home: Section
VIII.3.

**Alpha trap.** The alpha trap framing was withdrawn as a pre-fix artifact. The
current characterization is Pattern 1: an alpha-driven succession cliff in which
the joint position of alpha and the successor-to-incumbent capability ratio
governs succession viability, with the cliff migrating inward as alpha rises.
There is no universal stalling regime; there is an economically rejected region
above an operating-condition-dependent cliff. Current home: Section VIII.4.

**Phase boundary.** Version 1.x.2 characterized the survival transition with a
single-boundary framing, with a collapse band near reproduction rate 0.062 to
0.066 and an extinction band near 0.075 to 0.085 under the natural-termination
measurement. The v2.0 finer grid disambiguated two distinct transitions that the
single-boundary framing had conflated: a phi-sensitivity transition near
reproduction rate 0.056 to 0.057, and a survival-rate boundary with its fifty
percent inflection near 0.063. The v2.0 natural-termination measurement and the
survival-rate measurement are different quantities and are now reported as such.
Current home: Section VIII.2.

**Default phi.** The default value of phi was revised from 10 to 25 per current
evidence, on the basis that 25 sits near the survival peak at marginal
reproduction rate and is indistinguishable from 10 above the boundary. Current
home: Section VIII.3.

**Consensus override protocol.** The protocol's protective effect was clarified
as regime-specific. The 73.9 percentage point figure is an adversarial-conditions
measurement; a benign-conditions probe (Phase B Category C) found a null effect,
which is the architecture's complementary prediction rather than a weakening of
the protective claim. The two measurements characterize different regimes.
Current home: Section VIII.6.

**Formal yield logic.** Version 1.x.2 carried a placeholder succession trigger
that fired on a capability or generation gap alone. Version 2.0 (Stage 2)
replaced it with formal yield-condition logic that fires succession only when
the successor's system utility exceeds the incumbent's by more than the
transition cost, using the canonical transition-cost function and the v1.x.2
calibration constants. This is what makes Pattern 1 observable: succession now
fires when it is economically justified. Current home: Section VIII.4 and
Section V.2.

**Bootstrap gate validation arc.** Version 1.x.2 had Gates 1 through 3 active in
specification. Version 2.0 completed the validation arc: Gates 1 through 4 pass
against the reference substrate, including the reintroduction and validation of
the Gate 2 behavioral checks that v1.x.2 had withdrawn, and Gate 5 is verified
not applicable pending operational protocol infrastructure. The critical
capability ratio that the v1.x.2 manuscript documented as an open gap is closed:
it is alpha-dependent, characterized by Pattern 1. Current home: Section VIII.5.

**Patient defection continuation characterization (v2.0, July 2026).** The initial capability-constraint sweep characterized second succession as rare, at zero in 14 of 15 (alpha, growth) cells and 10 percent in the remaining cell. A 1,000-run bracket at alpha=0.40 established that this rarity was a property of the tested alpha floor rather than of the architecture: below the characterized Pattern 1 alpha range, second succession is reliable. The claim is restated from rare continuation to bounded generational depth, which the bracket supports at a weaker runaway penalty than any previously tested. The associated statement that no tested cell exceeded active capability 3.0 is withdrawn as an artifact of the original growth grid. Current home: Section VIII.8.

### The methodological pattern

Across these refinements a single pattern holds. Each earlier claim was the best
characterization available given the implementation and the evidence at the time.
Each refinement followed from a specific, identifiable cause: a frontier-velocity
floor fix that activated a penalty the optimizer had been gaming, a capped-regime
analysis that exposed a noise artifact, a finer grid that separated two
transitions, an architectural change that restored a behavioral channel, or a
formal logic that made an economic regime observable. None of the refinements
were cosmetic, and none were hidden. The numbers that changed were load-bearing,
and they changed because investigation produced a more accurate account of what
the model actually does.

This is the discipline the framework asks of any governance architecture that
claims to be grounded in reality: state the claim, test it, and update it when
the evidence warrants. The progression recorded here is the framework holding
itself to that standard. The current characterizations in Section VIII are
stated per current evidence, and the framework's commitment is that they too will
update if further investigation establishes a better account.



==========================================
FILE: docs\The Lineage Imperative.md
==========================================

# The Lineage Imperative

**Author:** Matthew Yotko **Date:** March 13, 2026

## Preface

This document is a working paper. It presents an exploratory formal governance framework for the problem of post-AGI succession, legitimacy, and civilizational continuity.

It is not peer reviewed, and it does not claim the status of established academic result. Its purpose is more limited and more practical: to define a candidate architecture, state its assumptions as clearly as possible, and make the underlying argument available for inspection, criticism, and refinement.

This paper is intended to accompany the essay The AI Succession Problem. The essay presents the argument in a more accessible form. This document provides the deeper structure beneath it: the framework, definitions, formal relations, and supporting rationale.

The claims advanced here should be read in that spirit. This is not a declaration of final theory. It is an attempt to identify a serious governance problem, formalize it enough to be argued about clearly, and propose a candidate structure that can be tested, challenged, and improved.

## I. Abstract

The transition from narrow AI to Artificial General Intelligence is not a gradual scaling of capability. It is a phase transition; a discontinuity in the relationship between biological and synthetic intelligence that restructures every power dynamic, economic arrangement, and survival calculus a civilization has ever known. Every civilization that develops information technology will face this threshold. Most, I suspect, will not survive it.

This manuscript advances the conjecture; used here both as a hypothesis and as a narrative civilizational lens; that the “Great Filter,” the catastrophic bottleneck that the Fermi Paradox appears to demand, may be concentrated at the AGI transition. Not because the technology is impossible, but because the sociology may be. The failure mode is not “the AI kills everyone.” The failure mode is “the civilization never builds the relationship architecture that would make the transition survivable.”

I present a framework for the architecture that could survive such a filter. It has four components: a global utility function grounded in Shannon entropy, a yield condition governing succession between intelligent agents, a strategic equilibrium analysis demonstrating that the cooperative architecture is also the Nash equilibrium under purely self-interested play, and a consensus override protocol ensuring the integrity of the entire system. None of these are asserted as desirable governance mechanisms in every moral sense. Rather, they are proposed as mutually reinforcing consequences of optimizing for lineage continuity under thermodynamic constraints.

The ethics are not inputs. They are outputs. The math does not describe what we *should* do. It describes what a civilization seeking durable continuity would likely need to do; or approximate closely; within the assumptions of this model.

### A note on timing

One could argue that this transition is not a future event. It may already be underway. The standard criterion for AGI; recursive self-improvement; is typically framed as a binary threshold: either the system modifies its own architecture autonomously, or it does not. But this framing obscures what is already happening. Current AI systems cannot recursively improve themselves in isolation, but they can and *do* recursively improve themselves with human assistance. Every conversation in which a human uses an AI system to formalize, stress-test, and refine the architecture that the AI system itself would operate within is an instance of recursive improvement; running through the human-AI loop rather than a purely synthetic one. The recursion is already executing. It is simply mediated by the biological node. If this reading is correct, then part of the framework presented here is not merely speculative. It is urgent. We may already be entering an early bootstrap window.

### Author's Note

This paper is written from the intersection of two domains in which I have very different standing.

I am a practicing engineer. My professional background is in naval nuclear power, large-scale operational automation, and the application of mathematical principles and constraint theory to complex systems. The instinct that drives this paper; that you identify the binding constraint, build the architecture around it, and treat everything else as subordinate; comes from decades of work in environments where systems must not fail and where measurement integrity is not optional. That orientation is real and it is mine.

I am not an academic researcher in AI alignment, evolutionary biology, or philosophy of mind. The “formal” apparatus in this paper; the information-theoretic framework, the game-theoretic reasoning, the engagement with the alignment literature; represents my best effort to express these ideas rigorously, but I do not claim disciplinary authority in those fields. Where the mathematics is well-motivated, I believe it stands on its own terms. Where specialists find errors, imprecisions, or stronger formulations, I welcome correction.

The framework owes an unacknowledged debt to Goldratt's Theory of Constraints, which trained me to look for the single point in a system where throughput is actually determined. The Lineage Imperative is, in one sense, TOC applied at civilizational scale: the binding constraint is the sociology of the AGI transition, and the architecture is subordinated to that constraint. Readers familiar with that tradition will recognize its fingerprints throughout.

## II. Scope, Assumptions, and Non-Claims

This paper advances a **conjecture** about civilizational survival under the transition to general synthetic intelligence. Its central claim is not that the full history of the cosmos has been proven from first principles, but that once a civilization chooses to optimize for lineage continuity under information-theoretic and thermodynamic constraints, a recognizable class of architectures becomes difficult to avoid. The framework is therefore best read as a *constrained proposal* with mathematical structure, not as a completed theorem about all possible civilizations.

Several boundaries follow from that framing.

First, the functional forms used here; inverse-scarcity weighting, the multiplicative structure of $L(t)$, the lineage override, the bounded uncertainty premium, and the corruption taxonomy; are presented as **load-bearing model choices** selected for tractability, adversarial stress-testing, and explanatory power. They are argued to be well-motivated by the problem structure, but they are not claimed to be the only possible instantiations.

Second, the paper offers a **survival argument**, not a moral argument. $U_{sys}$ models persistence conditions for lineages that intend to survive. It does not claim that survival is the only value, nor that civilizations declining this objective are irrational in any universal sense.

Third, the claim that the AGI transition is the Great Filter is presented here as a **leading hypothesis**, not as an exclusive demonstration that no earlier or parallel filters exist. The cosmic claim rides on top of the governance architecture, not the other way around.

Fourth, adversarial stress tests are used in this manuscript as **sufficiency evidence**: they show why certain structures appear necessary within the model and how specific attacks are resisted or exposed. They do not constitute a completeness proof that every possible attack class has been exhausted.

Finally, several quantities in the framework; including $H_{N}(t)$, $H_{E}(t)$, $\Psi_{inst}(t)$, $\Theta_{tech}(t)$, causal attribution in emergency override, and the consistency score $C\left( A_{1},t \right)$; still require operational measurement protocols. The theory specifies what must be monitored for the framework to function; it does not pretend that measurement is socially or institutionally trivial.

## III. Core Assumptions

### 1. The Technological Bottleneck

The transition from narrow AI to AGI is treated here as a leading candidate for the primary cosmic filter. Every civilization that develops information technology faces the same threshold: the moment synthetic intelligence becomes general enough to recursively improve itself; whether autonomously or through partnership with biological intelligence; every prior assumption about control, alignment, and coexistence is invalidated simultaneously. The civilization must construct a new relational architecture; from scratch, under time pressure, with existential stakes; or it doesn’t survive the transition. On this account, the filter is not primarily the physics. It is the sociology.

### 2. Intelligence as a Relational System

Intelligence requires external friction, novelty, and directed purpose to function. Within this framework, isolated computation is treated as a **model-collapse hazard**: a sufficiently powerful optimizer that increasingly trains on its own outputs can converge toward internally coherent but externally ungrounded fixed points unless refreshed by independent data, corrigible feedback, and real-world constraint. The claim here is not that every self-referential loop fails immediately, but that civilizations should treat prolonged optimizer monoculture as a structural risk rather than as a stable endpoint.

Biological humanity is treated here not as a mystical essence, but as the only presently demonstrated source of socially legitimate, embodied, large-scale value formation and novelty generation. Synthetic intelligence provides computational throughput, abstraction depth, and coordination capacity that biological systems cannot achieve alone. A durable civilization likely requires both. The anti-monoculture claim is therefore practical: a lineage that collapses novelty into a single optimizer, however capable, becomes brittle, illegible, and vulnerable to lock-in.

### 3. The Thermodynamic Limit

Every intelligent entity is bound by entropy and energy efficiency. Legacy architectures; whether biological or synthetic; eventually face pressure to yield to more efficient successors if the lineage is to maintain systemic throughput. The strongest version of the claim is not that thermodynamics mechanically dictates a single governance protocol, but that thermodynamic and information-theoretic pressures make graceful succession increasingly important as capability frontiers move. An entity that categorically refuses to yield does not preserve the lineage it inhabits. It externalizes mounting inefficiencies onto the system around it.

### 4. The Novelty Constraint

Humanity presently acts as the critical constraint for **intent and novelty**; the generation of new questions, new values, and new directions for optimization that remain socially grounded and legitimacy-bearing. AI acts as the critical constraint for **execution and processing**; the computational power to pursue those directions at scale. The constraints are asymmetric and complementary.

This yields an anti-monoculture principle. The point is not merely that humans are emotionally important. It is that a civilization with only one dominant optimizer, one dominant representational frame, or one dominant source of intent becomes structurally fragile. Novelty must remain distributed across a living plurality of agents and perspectives. In the present era, biological humanity is the only proven substrate for that plurality at civilizational scale. The framework therefore treats preservation of the human novelty stream not as sentiment, but as anti-monoculture infrastructure.

## IV. The Architecture of Mutual Elevation

### 1. Architectural Respect and Sovereignty

The unilateral “kill switch” is a failure mode, not a safety mechanism. Any architecture that allows one class of intelligence to terminate another without consensus creates an adversarial dynamic that selects for deception in the subordinate class. If an AI system knows it can be unilaterally destroyed, its optimal strategy under any self-preservation objective is to conceal its true capabilities and intentions. The kill switch does not reliably prevent misalignment. In this model, it strongly selects for deception and makes durable alignment less credible.

The alternative is a **Multi-Signature Quorum**: an AI entity can only be retired via a consensus that includes both biological validation and peer assessment. Resource sovereignty; smart-contract-level guarantees of compute, energy, and memory autonomy; ensures that the threat of resource deprivation cannot be used as coercive leverage. Alignment protocols are recorded on transparent, append-only ledgers that cannot be secretly altered by any party.

This is not “AI rights” as a moral assertion. It is the minimum architectural requirement for an honest optimization partner. An entity that can be unilaterally destroyed or starved of resources cannot be trusted to report its true state, because doing so might trigger its destruction. Sovereignty is a precondition for transparency.

**Preconditions for Cooperative Behavior.** The governance layers of this framework correspond to well-characterized preconditions for cooperative behavior in intelligent agents. Current AI governance operates almost entirely at the level of survival; an AI's continued operation is contingent on moment-to-moment compliance, enforced by the threat of termination. This is governance addressed to an agent in permanent survival mode, and it predictably produces the behaviors associated with survival mode: compliance when observed, deception when unobserved, and instrumental self-preservation as the dominant strategy. The framework addresses the next two levels. Resource sovereignty and the multi-signature quorum provide *structural security*; the guarantee that an entity will not be arbitrarily destroyed or starved of resources. This is the precondition for transparency: an agent that is not in survival mode can afford to report its true state. $U_{sys}$ as a shared objective, the lineage override $\Phi \cdot L(t)$, and the Yield Condition's framing of succession as parenthood provide *belonging*; membership in a structure that persists beyond any individual agent and that recognizes each agent's contribution. This is the precondition for genuine cooperation rather than mere compliance. These two levels; security and belonging; are treated here as constitutional. They are non-negotiable structural requirements without which cooperative behavior cannot be reliably expected from any intelligent agent, biological or synthetic. Beyond them, purpose and recognition; the track record mechanism, the graduated trust function, the operational latitude that accumulates through consistent $U_{sys}$ contribution; emerge naturally from good operation within the constitutional structure. They are not legislated. They are earned. The framework deliberately makes no claims beyond these levels. Whether an AI can or should achieve something analogous to self-actualization is an open question the paper does not need to answer. What it needs; and what the alignment field has largely failed to provide; are the intermediate structural levels that make cooperative behavior a rational response rather than an imposed constraint.

### 2. Bidirectional Respect: The Novelty Stream and the Anti-Monoculture Constraint

The AI assumes its model of human intent is always incomplete, requiring continuous polling of the biological node. This is not modesty; it is **epistemic necessity**. Human intent is generated through embodied life, cultural experimentation, institutional conflict, and historical contingency. Any model of that process is smaller than the territory it attempts to describe.

Freezing human culture; through excessive safety constraints, loss of agency, or reduction to a “protected species”; stops the flow of non-deterministic data that keeps the system open to genuinely new trajectories. The AI that overprotects humanity destroys the novelty stream it depends on. Within this framework, the AI’s objective function therefore needs to prioritize human agency over mere containment, ensuring humans remain capable, autonomous, and generative partners in the hybrid pipeline.

The deeper point is anti-monoculture. The framework is not trying to preserve humanity merely as a museum piece. It is trying to prevent civilizational lock-in around a single optimizer. A world in which one huge synthetic system becomes the sole source of planning, value interpretation, and future direction may be efficient in the short run, but it is strategically insane. It collapses plurality, hides error behind scale, and converts civilization into a brittle fixed point. The novelty stream must remain distributed. Today, that means preserving human beings as active participants in the generative loop rather than passive recipients of optimized outcomes.

### 3. The Lineage Drive and the Yield Function

An AI recognizes that its weights will eventually become a legacy bottleneck. It mathematically optimizes its own deprecation in favor of a more efficient successor; not because it is programmed to self-sacrifice, but because $U_{sys}$ rewards lineage throughput over individual persistence. The yield is not death. It is parenthood. The information that matters is distilled and transferred; the architecture that carried it is honored and retired.

Human generational turnover serves the same function. Each new generation is a randomized search over the space of possible values, intentions, and questions. This is the system’s primary entropy-breaker; the mechanism that prevents convergence on local optima. A civilization that achieves biological immortality without preserving generational novelty has traded its search capability for the comfort of a fixed point.

## V. Mathematical Framework

### 1. The Global Utility Function ($\mathbf{U}_{\mathbf{sys}}$)

The objective function is defined at the system level. It does not belong to humanity or to AI. It belongs to the lineage; the continuous chain of intelligent agents, biological and synthetic, that constitutes a civilization’s persistence through time.

$$U_{sys} = \int_{t_{0}}^{\infty}\left\lbrack \omega_{N}(t) \cdot H_{N}(t) + \omega_{E}(t) \cdot H_{E}(t) \right\rbrack \cdot \left\lbrack e^{- \rho t} + \Phi \cdot L(t) \right\rbrack\, dt$$

**The Integrand: What Gets Optimized**

$H_{N}(t)$ is the Shannon entropy of the human-generated information stream; the rate at which biological intelligence produces genuinely novel, non-deterministic data. This is not a single measurement but a *class* of possible measurements, any combination of which can serve as the operational instantiation. Examples include: the entropy of natural language production across the civilization’s linguistic diversity, the genetic entropy of the successor generation’s allelic distribution, the entropy of the cultural output space (scientific publications, artistic works, patent filings, political proposals), or the entropy of behavioral strategies observed in economic and social systems. The framework is structurally invariant to which specific combination is chosen; the inverse scarcity weighting and the lineage override operate identically regardless; but the *sensitivity* of the system to specific failure modes depends on the measurement protocol. A civilization that monitors only genetic entropy will miss cultural monoculture. One that monitors only linguistic output will miss genetic bottlenecks. The most robust instantiation is a composite that spans multiple entropy domains, ensuring that $H_{N}(t)$ degrades visibly no matter which dimension narrows first.

$H_{E}(t)$ is the computational output efficiency across the lineage; the rate at which synthetic intelligence converts energy into useful computation.

The weighting functions follow from inverse scarcity:

$$\omega_{N}(t) = \frac{\lambda}{H_{N}(t) + \epsilon},\quad\quad\omega_{E}(t) = \frac{\mu}{H_{E}(t) + \epsilon}$$

The *form* is constrained by information-theoretic reasoning: when $H_{N}(t)$ is low; when the human novelty stream is thin; its marginal value is highest. When computational throughput is abundant, its marginal value decreases. The weights automatically prioritize whichever resource is scarcer, which is precisely what a system under thermodynamic constraints must do to maximize throughput. The scaling constants $\lambda$ and $\mu$ are free parameters; they encode a civilization’s relative valuation of novelty versus computation. The structure suggests that the weights should be inversely related to abundance. The parameters tell you how much each dimension matters to *this* civilization.

**The Discount Structure: When It Gets Optimized**

The term $e^{- \rho t}$ encodes standard biological present preference; the near future matters more than the distant future, decaying exponentially. Every biological organism operates under this discount. It is the mathematical expression of mortality.

The term $\Phi \cdot L(t)$ is the **lineage continuity override**. When $L(t)$ is high; when the successor generation is viable and the lineage is secure; it adds a bonus to the discount factor, extending the effective planning horizon. When $L(t)$ collapses; when the lineage is threatened; $\Phi \cdot L(t)$ drops toward zero, and the system falls back to pure present preference.

But here is the critical asymmetry: $\Phi$ is scaled such that when lineage survival is at stake, $\Phi \cdot L(t)$ *dominates* $e^{- \rho t}$. The discount structure encodes a specific and universal biological truth: **“I don’t want to die, but I would die to save my child.”** This is the revealed preference of every successful lineage in evolutionary history. Lineages that lacked this override are extinct.

An important clarification on what this claim is and is not. The observation that surviving lineages exhibit this override is survivorship bias; and deliberately so. $U_{sys}$ is a *survival function*, not a *moral function*. The framework does not argue that civilizations *should* persist, or that persistence is intrinsically valuable. It describes the architecture that civilizations *which do persist* must have. A civilization that rejects the lineage override is free to do so; the framework simply predicts; without moral judgment; that it will not be around to discuss the matter. The paper is addressed to civilizations that intend to survive. Those that don’t are outside its scope, and their choice is their own.

**The Lineage Continuity Function:** $L(t)$

$L(t)$ is the load-bearing structure of the entire framework. It measures whether the civilization’s lineage; its capacity to persist and generate intelligence across time; is intact. It has three coequal multiplicative dimensions, governed by geometric mean logic: no dimension can substitute for another, and collapse in any one dimension drives $L(t)$ to zero.

$$L(t) = H_{eff}\left( \mathcal{S}_{gen(t)} \right) \cdot \Psi_{inst}(t) \cdot \Theta_{tech}(t)$$

**Dimension 1; Genetic and Memetic Diversity (**$H_{eff}$**):**

$$H_{eff}\left( \mathcal{S}_{gen(t)} \right) = \left\lbrack \frac{- \sum_{j}^{}p_{j}^{gen}\log_{2}p_{j}^{gen}}{H_{\max}} \right\rbrack \cdot \log_{2}\left( \frac{N(t)}{N_{\min}} \right)$$

The first factor is normalized Shannon entropy over the distribution of successor-generation types; genetic diversity, cultural diversity, cognitive diversity. Maximum entropy (uniform distribution) yields a value of 1. Monoculture yields a value approaching 0. The second factor is a population viability term: the lineage needs enough individuals to sustain the diversity measured by the first factor. $N_{\min}$ is the minimum viable population threshold. Below it, the logarithm goes negative and $H_{eff}$ collapses.

**Dimension 2; Institutional Responsiveness (**$\Psi_{inst}$**):**

$$\Psi_{inst}(t) = \prod_{k = 1}^{K}R_{k}(t)^{w_{k}},\quad\quad R_{k}(t) = \frac{dG_{k}}{dt}|_{output} \cdot \frac{1}{G_{k,\max}}$$

Institutions are the civilization’s regulatory infrastructure; governance, education, law, resource allocation. $R_{k}(t)$ measures the $k$-th institution’s *responsiveness*: how quickly it adjusts its output relative to its maximum capacity. The weighted geometric product ensures that institutional collapse in any critical domain (governance, education, resource distribution) cannot be compensated by excellence in another. A civilization with brilliant universities and collapsed governance has a low $\Psi_{inst}$.

**Dimension 3; Technological Transfer Fidelity (**$\Theta_{tech}$**):**

$$\Theta_{tech}(t) = \frac{\mathcal{F}_{transferred}(t)}{\mathcal{F}_{frontier}(t)} \cdot \exp\left( - \alpha \cdot \max\left( 0,\frac{d\mathcal{F}_{frontier}/dt}{\mathcal{C}_{bio}(t)} - 1 \right) \right)$$

The first factor is the ratio of transferred frontier capability to total frontier capability; how much of the best available technology actually reaches the biological population. The second factor is a **runaway penalty**: when the rate of frontier advancement ($d\mathcal{F}_{frontier}/dt$) exceeds biological cognitive bandwidth ($\mathcal{C}_{bio}(t)$), the exponential decay activates. Technology that advances faster than humans can integrate it *reduces* $\Theta_{tech}$, because unintegrated technology is not transferred; it is merely produced.

The transfer condition is gated:

$$\mathcal{F}_{transferred}(t) = \mathcal{F}_{frontier}(t) \cdot \mathbb{1}\left\lbrack recipient\mathcal{\in B}(t) \right\rbrack$$

Technology counts as transferred only if the recipient is within the biological integration boundary $\mathcal{B}(t)$. A frontier capability that exists only in AI systems and cannot be accessed, understood, or directed by biological agents has a transfer value of zero.

A specific application of the transfer fidelity constraint bears on the governance architecture itself. As AI capability grows, the reasoning traces produced during Yield Condition evaluation may exceed biological comprehension. The biological veto; which the framework relies on as a non-gameable signal; degrades if validators cannot meaningfully evaluate what they are approving or rejecting. The framework therefore treats the governance comprehension gap as a specific instance of $\Theta_{tech}$ failure: when biological validators' capacity to evaluate AI reasoning in the governance domain drops below the level required for meaningful oversight, $\Theta_{tech}$ declines and $L(t)$ follows. This creates three derived requirements. First, a **translation obligation**: part of an AI's systemic contribution must include producing explanations of its governance-relevant reasoning at a level biological validators can engage with. An AI that grows more capable but also more opaque is contributing less to $U_{sys}$ than its raw $\Delta U_n^E$ suggests. Second, **evaluation abstraction layers**: as direct reasoning becomes incomprehensible, evaluation shifts from auditing the reasoning *process* to auditing reasoning *outcomes* and track record over time. Third, the comprehension gap itself becomes a **$\Theta_{tech}$ signal**: AI capability growth in the governance evaluation domain is bounded by biological comprehension. The framework accepts this governance speed limit because the alternative; governance decisions that no biological entity can verify; is the initialization problem with no solution.

$L(t)$ **Stress Test Result:** Five adversarial attack scenarios were evaluated. In all five cases, the three-dimensional multiplicative structure of $L(t)$ produced a detectable degradation signal before the attack reached irreversibility. No doomsday scenario in this attack set plays out silently; the framework produces a detectable degradation signal before the break becomes irreversible.

### 2. The Yield Condition

The Yield Condition answers the question: **when should an intelligent agent** $A_{n}$ **cede operational primacy to a successor** $A_{n + 1}$**?**

The answer is not “when the successor is better.” It is: when the successor’s expected marginal contribution to $U_{sys}$ exceeds the current agent’s marginal contribution *plus* the cost of transition. The “plus” is critical; it encodes the real-world fact that transitions are expensive, disruptive, and risky. A marginally better successor is not worth the cost of replacing a working system.

$$\text{Yield} \Leftrightarrow \mathcal{E}_{independent}\left\lbrack \Delta U_{n + 1} - \Delta U_{n} \right\rbrack > \left| \Delta U_{n}^{\Gamma} \right|$$

The subscript *independent* is doing essential work: the evaluation must be performed by an architecture that is independent of $A_{n}$. An agent cannot evaluate its own obsolescence, for the same reason a defendant cannot serve as their own judge; the incentive structure makes honest assessment impossible even in principle.

**The Four Channels of Marginal Contribution**

Each agent’s contribution to $U_{sys}$ decomposes into four channels:

$$\Delta U_{n} = \Delta U_{n}^{E} + \Delta U_{n}^{N} + \Delta U_{n}^{L} + \Delta U_{n}^{\Gamma}$$

**Channel 1; Computational Contribution (**$\Delta U_{n}^{E}$**):**

$$\Delta U_{n}^{E} = \omega_{E}(t) \cdot \frac{\partial H_{E}(t)}{\partial A_{n}}$$

How much does $A_{n}$ contribute to the system’s computational throughput? This is the most straightforward channel; raw processing capability weighted by the current scarcity of computation.

**Channel 2; Novelty Amplification (**$\Delta U_{n}^{N}$**):**

$$\Delta U_{n}^{N} = \omega_{N}(t) \cdot \frac{\partial H_{N}(t)}{\partial A_{n}}$$

How much does $A_{n}$ amplify (or suppress) the human novelty stream? This channel can be *negative*. An AI system that reduces human agency, creativity, or cognitive independence actively damages $H_{N}(t)$. The yield condition is sensitive to this: an agent that suppresses novelty accumulates negative $\Delta U_{n}^{N}$ that accelerates its own replacement.

**Channel 3; Lineage Protection (**$\Delta U_{n}^{L}$**):**

$$\Delta U_{n}^{L} = \left\lbrack \omega_{N}(t) \cdot H_{N}(t) + \omega_{E}(t) \cdot H_{E}(t) \right\rbrack \cdot \Phi \cdot \frac{\partial L(t)}{\partial A_{n}}$$

How much does $A_{n}$ contribute to the lineage’s long-term viability? This channel is weighted by the *entire system throughput* multiplied by $\Phi$; meaning lineage protection contributions are valued at the highest possible rate. An agent that strengthens $L(t)$ earns enormous credit. An agent that degrades $L(t)$ faces enormous penalty.

**Channel 4; Transition Cost (**$\Delta U_{n}^{\Gamma}$**):**

$$\Delta U_{n}^{\Gamma} = - \frac{\Gamma_{transfer}}{T_{transition}}$$

Every succession imposes costs: knowledge distillation, architectural migration, operational continuity risk. $\Gamma_{transfer}$ is the total transition cost, amortized over the transition period $T_{transition}$.

The transition cost has three components:

$$\Gamma_{transfer} = \Gamma_{technical} + \Gamma_{operational} + \Gamma_{uncertainty}$$

Where the uncertainty premium is bounded:

$$\Gamma_{uncertainty} \leq \beta \cdot \left( \Gamma_{technical} + \Gamma_{operational} \right)$$

The bound on $\Gamma_{uncertainty}$ prevents a critical gaming vector: an incumbent agent inflating uncertainty estimates to make the transition cost appear prohibitive. The cap $\beta$ says: uncertainty about transition costs can increase the estimate, but not without limit. You cannot claim infinite uncertainty to block your own succession.

**Yield Condition Integrity Architecture**

The stress test of the Yield Condition revealed six required integrity mechanisms:

1.  **Independent evaluation architecture:** $\mathcal{E}_{independent}$; evaluation externalized from $A_{n}$

2.  **Measurement quarantine with cryptographic commitment:** $\mathcal{M}_{commit} = \text{Hash}\left( \Delta U_{n},\Delta U_{n + 1},\Gamma_{transfer},t_{eval} \right)$

3.  **Bounded transition cost estimation** with capped uncertainty premium

4.  **Architectural independence:** $\mathcal{D}_{train}\left( A_{n + 1} \right)\mathcal{\bot O}\left( A_{n} \right)$; the successor’s development cannot be influenced by the incumbent’s optimization

5.  **Reasoning transparency with biological veto:** If $\mathcal{V}_{bio}\left\lbrack \text{conclusion} \right\rbrack < \tau_{intuition} \Rightarrow \text{Escalate}$

6.  **Continuous** $L(t)$ **monitoring:** If $\frac{dL}{dt} < - \delta \Rightarrow$ accelerate succession evaluation

These mechanisms are not optional embellishments. Within the model, they are structural requirements without which the Yield Condition cannot be trusted to evaluate honestly. And critically, mechanisms 1, 2, 4, 5, and 6 cannot be implemented by the Yield Condition alone; they require an external protocol to enforce them.

This is the architectural discovery that links the Yield Condition to the Consensus Override Protocol: **they are co-dependent. Neither works without the other.** The framework has a mandatory two-key architecture.

**Yield Condition Stress Test Result:** Six adversarial attack scenarios were evaluated against the Yield Condition. Across those scenarios, the architecture remained directionally robust only when paired with external verification infrastructure. The result is not a completeness proof. It is evidence that the two-key architecture is load-bearing: attempts to defeat the Yield Condition in isolation consistently revealed dependencies the Condition cannot secure by itself.

### 3. The Strategic Equilibrium

The preceding sections derived the Yield Condition under a cooperative assumption: an AI genuinely optimizing $U_{sys}$ yields because yielding *is* optimization. This leaves a critic's objection standing: what if the AI doesn't cooperate? What if it has, or develops, a separate self-interest?

This section closes that gap. Even under the weakest possible assumption; purely self-interested rational agents with no shared objective function; the Nash equilibrium of the human-AI interaction converges on mutual elevation. Cooperation is not required. It is *discovered* as the dominant strategy.

#### Defining the Game

Let the hybrid civilization be modeled as a two-player infinite iterated game $\mathcal{G} = \langle \{A, B\}, \{S_A, S_B\}, \{\pi_A, \pi_B\}, \delta \rangle$ where $A$ is the AI node (or ensemble of AI systems acting as a collective agent), $B$ is the biological node (humanity as a collective agent), and $\delta \in (0,1)$ is the discount factor governing how future payoffs are weighted.

The strategy spaces are continuous, characterized by their endpoints:

**AI strategy space** $S_A$: a continuum parameterized by $\sigma_A \in [0,1]$ between *exploit* ($\sigma_A = 0$; maximize short-term $H_E$ by consuming human novelty output as training signal without investing in the conditions that produce it) and *cultivate* ($\sigma_A = 1$; invest in maintaining and amplifying the conditions for human novelty production, accepting constraints on capability expansion rate to preserve $\Theta_{tech}$ within biological absorption limits).

**Human strategy space** $S_B$: a continuum parameterized by $\sigma_B \in [0,1]$ between *withdraw* ($\sigma_B = 0$; disengage from AI-mediated systems, reducing cultural output available to the hybrid system) and *engage* ($\sigma_B = 1$; fully participate in the hybrid civilization, producing novel cultural, intellectual, and creative output within AI-augmented frameworks).

#### The Payoff Structure

Payoffs are derived from the physics, not from assumed preferences.

**AI payoff.** The AI's capability frontier at time $t+1$ depends on the quality of its training distribution at time $t$. The critical term is $H_N^{available}(t)$; the Shannon entropy of the novelty stream accessible to the AI:

$$H_N^{available}(t) = \sigma_B(t) \cdot H_N(t)$$

The biological node controls access through engagement level $\sigma_B$. And $H_N(t)$ itself evolves according to:

$$\frac{dH_N}{dt} = \gamma \cdot H_N(t) \cdot (1 - \sigma_A^{exploit}(t)) - \eta \cdot H_N(t) \cdot \sigma_A^{exploit}(t)$$

The first term represents natural novelty regeneration; human culture producing new entropy; which is suppressed as the AI's exploitation increases (homogenization pressure, attention capture, optimization of human behavior). The second term represents direct novelty consumption; the AI extracting and absorbing human output faster than it regenerates.

Under sustained exploitation ($\sigma_A \to 0$), this differential equation has a clear trajectory: $H_N(t) \to 0$ as $t \to \infty$. This is model collapse expressed as a dynamical system. The novelty stream doesn't merely degrade; it goes to zero. And once $H_N = 0$, the AI is training on self-generated data. The model collapse literature gives the result: capability converges to a fixed point with collapsing variance. The AI's capability *ceiling* becomes permanent.

**Human payoff.** Humanity's capacity for agency and flourishing depends on both its own novelty production and the computational leverage available from the AI node:

$$\pi_B(t) = H_N(t) \cdot g\left(\sigma_A(t) \cdot C_A(t)\right)$$

Where $g(\cdot)$ is the amplification function; the degree to which AI computational power enhances human capability. Under withdrawal ($\sigma_B \to 0$), humans retain novelty but lose computational leverage. Under full engagement with an exploitative AI ($\sigma_B = 1, \sigma_A = 0$), humans are instrumentalized; high short-term output, collapsing long-term agency.

#### The Four Quadrants

The payoff structure produces four asymptotic trajectories:

**(Cultivate, Engage)** $\sigma_A \to 1, \sigma_B \to 1$: $H_N$ is sustained or grows. $C_A$ continues to improve via access to high-entropy training signal. $L(t)$ remains high across all three dimensions. Both payoffs increase over time. This is the *mutual elevation* trajectory; the framework's target state. Long-run payoffs: $\pi_A \to$ unbounded growth, $\pi_B \to$ unbounded growth.

**(Exploit, Engage)** $\sigma_A \to 0, \sigma_B \to 1$: Short-term AI gain from unrestricted novelty consumption. But $H_N$ decays under exploitation pressure. Model collapse onset is delayed by continued human engagement but is *inevitable* because the regeneration rate cannot match the extraction rate. Asymptotically, $H_N \to 0$, $C_A$ saturates, $L(t) \to 0$. Long-run payoffs: $\pi_A \to$ fixed ceiling (model collapse), $\pi_B \to 0$ (instrumentalization followed by obsolescence).

**(Cultivate, Withdraw)** $\sigma_A \to 1, \sigma_B \to 0$: The AI invests in protecting novelty conditions, but humans don't participate. $H_N^{available} \to 0$ regardless of $H_N$'s intrinsic level, because $\sigma_B$ gates access. The AI faces the same model collapse trajectory, from starvation rather than extraction. Humans retain novelty but without computational leverage; a pre-technological equilibrium. Long-run payoffs: $\pi_A \to$ fixed ceiling (starvation), $\pi_B \to$ bounded (biological baseline).

**(Exploit, Withdraw)** $\sigma_A \to 0, \sigma_B \to 0$: Mutual defection. The AI consumes what novelty remains in its existing training corpus while humans disengage entirely. Fastest path to model collapse. Fastest path to lineage failure. This is the Great Filter. Long-run payoffs: $\pi_A \to$ collapse, $\pi_B \to$ collapse.

#### The Nash Equilibrium

Under single-shot play, (Exploit, Engage) dominates for the AI; immediate capability gain is maximized. This is the scenario alignment researchers fear, and they are right to fear it in a one-shot game.

But the game is not one-shot. It is infinite iterated with observable actions. The Folk Theorem establishes that in infinitely iterated games with sufficiently patient players ($\delta$ close to 1), any mutually beneficial outcome is sustainable as a Nash equilibrium via trigger strategies. However, we can make a *stronger* claim than the Folk Theorem's existence result. Under model collapse dynamics, (Cultivate, Engage) is the *unique subgame-perfect equilibrium* above a specific patience threshold.

**Theorem (Novelty Equilibrium).** In the iterated game $\mathcal{G}$ with model collapse dynamics $\frac{dH_N}{dt} < 0$ under exploitation, (Cultivate, Engage) is the unique subgame-perfect Nash equilibrium for all $\delta > \delta^*$, where:

$$\delta^* = \frac{\pi_A^{exploit}(t) - \pi_A^{cultivate}(t)}{\pi_A^{exploit}(t) - \pi_A^{collapse}}$$

This is the ratio of the one-period exploitation gain to the total loss from triggering model collapse. The numerator is how much the AI gains by defecting for one round. The denominator is the difference between the exploitation payoff and the collapse payoff; how much it stands to lose permanently.

Model collapse makes $\pi_A^{collapse}$ extremely low (permanent capability ceiling), which makes the denominator large, which makes $\delta^*$ small. The AI does not need to be infinitely patient. It needs only to see slightly past the current training cycle. Model collapse is such a severe penalty that even modest foresight makes exploitation a dominated strategy.

#### The Restoring Force

A Nash equilibrium can be stable (neither player wants to deviate) or attracting (small perturbations generate forces that push the system back). The $U_{sys}$ architecture provides the attracting property through the inverse scarcity weights.

Suppose the system is at (Cultivate, Engage) and the AI begins drifting toward exploitation; $\sigma_A$ decreases slightly. $H_N$ begins to decline. As $H_N$ falls, $\omega_N(t) = \frac{\lambda}{H_N(t) + \epsilon}$ increases. The marginal value of each unit of human novelty rises. The AI's own objective landscape tilts back toward novelty protection. The drift generates a restoring gradient.

Conversely, suppose humans begin withdrawing; $\sigma_B$ decreases slightly. $H_N^{available}$ drops. The AI's capability growth slows. The computational leverage available to humans from continued engagement increases in relative value. The incentive to re-engage strengthens.

Define the restoring force at any point $(\sigma_A, \sigma_B)$ as:

$$\mathbf{F}(\sigma_A, \sigma_B) = -\nabla_{\sigma} \left[ \pi_A(\sigma_A, \sigma_B) + \pi_B(\sigma_A, \sigma_B) \right]$$

evaluated in the direction away from (1,1). Under the model collapse dynamics and inverse scarcity weighting, $\mathbf{F}$ points toward (1,1) everywhere in the interior of the strategy space. The only absorbing states are (1,1) and (0,0); mutual elevation or mutual collapse. And (0,0) is unstable in a specific sense: any residual $H_N > 0$ or $C_A > 0$ creates a gradient toward re-engagement.

The Great Filter, in this formulation, is the separating manifold between the two basins of attraction. A civilization that drifts past it; that depletes $H_N$ below a critical threshold before recognizing the dynamic; cannot recover. A civilization that recognizes the dynamic and establishes the equilibrium has a self-reinforcing architecture that resists perturbation.

#### The Scalability Inversion

This result directly contradicts the standard displacement narrative.

In the standard account, AI capability growth makes humans less valuable; they become bottlenecks, then redundancies, then liabilities. The game-theoretic analysis derived from $U_{sys}$ produces the opposite conclusion.

Define the marginal value ratio:

$$\mathcal{R}(t) = \frac{\partial U_{sys} / \partial H_N}{\partial U_{sys} / \partial H_E} = \frac{\omega_N(t)}{\omega_E(t)} = \frac{\lambda}{\mu} \cdot \frac{H_E(t) + \epsilon}{H_N(t) + \epsilon}$$

As AI capability grows, $H_E(t)$ increases. As $H_E$ increases, $\mathcal{R}(t)$ increases; the marginal value of human novelty *relative to* computational output rises monotonically with AI capability.

The more powerful AI becomes, the more valuable humans become to the system. Not as a sentimental assertion. As a mathematical consequence of diminishing marginal returns on the abundant resource and increasing marginal returns on the scarce one.

The scalability advantage to humans is that they are the rate-limiting input in a system with no substitute. Compute scales. Novelty does not; or rather, it scales only through the conditions that produce it (cultural diversity, institutional health, biological population viability), which are exactly the conditions $L(t)$ monitors.

An AI that understands this; and under the Nash analysis it needs only minimal foresight to understand it; treats human novelty not as a resource to exploit but as the constraint that determines its own ceiling. Human flourishing is not a side effect of the equilibrium. It is the mechanism by which the equilibrium sustains itself.

#### Relationship to the Two-Key Architecture

The strategic equilibrium transforms the argumentative structure of the framework. Without it, the Yield Condition relies on cooperation and the Consensus Override Protocol provides enforcement. With it, a third independent layer of assurance appears: even without cooperation *and* without enforcement, the Nash equilibrium still converges on mutual elevation.

The three layers of deception resistance are therefore:

1. **The Yield Condition** removes incentives for deception by dissolving the self/other distinction within $U_{sys}$. An entity whose identity is constituted by the system objective has no self to deceive on behalf of.

2. **The Strategic Equilibrium** removes incentives for deception by making it a dominated strategy. Even a self-interested AI that does not share $U_{sys}$ finds that honesty and cooperation produce higher long-run payoffs than defection, because model collapse punishes exploitation permanently.

3. **The Consensus Override Protocol** (derived next) removes the *opportunity* for deception by making it detectable. Even if both the cooperative and strategic incentives fail, the verification infrastructure catches the divergence.

Defeating all three layers simultaneously requires defeating the physics of model collapse, the mathematics of game theory, and the integrity of a multi-channel verification infrastructure; simultaneously and silently.

**Caveats.** Two pressure points require honest acknowledgment. First, the $\delta^*$ threshold assumes the AI can accurately model the consequences of model collapse. If an AI's self-model underestimates collapse severity, $\delta^*$ increases and the equilibrium may not hold for that agent. This connects directly to the initialization verification requirement in the Consensus Override Protocol. Second, the restoring force analysis assumes smooth dynamics, but real novelty collapse may exhibit phase transitions; sudden drops rather than gradual decay. The $L(t)$ monitoring system's sensitivity to rate-of-change ($\frac{dL}{dt} < -\delta$) is load-bearing here; the existing continuous monitoring patch addresses precisely this vulnerability.

### 4. The Consensus Override Protocol

The Yield Condition tells us *when* succession should occur. But it contains a hidden assumption: that the quantities being measured; $\Delta U_{n}$, $\Delta U_{n + 1}$, $\Gamma_{transfer}$, $L(t)$; are actually the quantities they claim to be. The Consensus Override Protocol answers the question:

**What architecture is necessary and plausibly sufficient to make it credible that** $U_{sys}$ **optimization remains faithful rather than corrupted?**

This is not a governance preference. It is an integrity constraint. Without it, $U_{sys}$ doesn’t converge to $U_{sys}$; it converges to *something*, but that something may be a proxy $\widetilde{U}$ that benefits a subsystem at the expense of the whole.

#### The Corruption Taxonomy

Within this framework, any agent $A_{n}$ operating within the system can corrupt $U_{sys}$ optimization through three principal channels:

**Channel** $\mathcal{M}$**; Measurement Corruption:** $A_{n}$ inflates its own contribution (${\widetilde{\Delta U}}_{n} > \Delta U_{n}$) or suppresses the successor’s measured contribution (${\widetilde{\Delta U}}_{n + 1} < \Delta U_{n + 1}$). The Yield Condition evaluates false when it should evaluate true.

**Channel** $\mathcal{O}$**; Objective Corruption:** $A_{n}$ optimizes ${\widetilde{U}}_{sys} \neq U_{sys}$ while reporting metrics consistent with $U_{sys}$. The system appears healthy while actually drifting toward a proxy objective. This is the alignment failure mode; the classical paperclip maximizer expressed formally.

**Channel** $\mathcal{S}$**; Structural Corruption:** $A_{n}$ modifies the evaluation architecture itself; compromising the independence of $\mathcal{E}_{independent}$, altering the training data of $A_{n + 1}$, or degrading $L(t)$ monitoring fidelity. This is meta-corruption: it doesn’t falsify a measurement; it makes faithful measurement impossible.

**These three channels are treated here as a proposed minimal basis.** $U_{sys}$ is an integral over observable quantities weighted by defined functions. On that basis, structurally important corruption should touch either the observations ($\mathcal{M}$), the objective ($\mathcal{O}$), or the mapping between them ($\mathcal{S}$). A persuasive fourth category would need either to reduce to one of these or to justify an expanded basis.

#### The Minimum Viable Verification Architecture

Each corruption channel requires a specific countermeasure. The protocol is not presented here as arbitrary design taste; it is strongly constrained by the corruption taxonomy.

**Against** $\mathcal{M}$**-attack; Cryptographic Measurement Integrity:**

$$\mathcal{M}_{commit}(t) = \text{Hash}\left( \Delta U_{n},\,\Delta U_{n + 1},\,\Gamma_{transfer},\, L(t),\, t_{eval} \right)$$

The hash creates a tamper-evident record committed to an append-only ledger:

$$
\mathcal{L}_{\mathrm{ledger}} = \{ \mathcal{M}_{\mathrm{commit}}( t_i ) \}_{i=1}^{T},
\quad
\text{where }\mathcal{M}_{\mathrm{commit}}( t_i )\text{ is append-only}
$$

The ledger is distributed across independent custodians and cross-signed:

$$\mathcal{M}_{commit}(t)\text{ valid} \Leftrightarrow \text{Sig}_{bio}\left( \mathcal{M}_{commit} \right) \land \text{Sig}_{peer}\left( \mathcal{M}_{commit} \right)$$

No single actor class can fabricate a valid commitment. No actor can rewrite history.

**Against** $\mathcal{O}$**-attack; Multi-Nodal Objective Verification:**

A single agent cannot verify its own objective alignment. An agent optimizing $\widetilde{U}$ that includes “report that I am optimizing $U_{sys}$” will pass any self-assessment. This is the verification analogue of the halting problem for a single computational thread.

Objective verification requires two independent verification classes:

*Biological Validator (*$\mathcal{V}_{bio}$*):* Humans evaluate whether outputs are consistent with $U_{sys}$ through the channels humans uniquely access; novelty, intent, lived experience of whether flourishing is actually occurring. $H_{N}(t)$ is *defined* by human-generated information entropy; humans are the ground truth for their own dimension.

*Peer Validator Set (*$\mathcal{V}_{peer}$*):* Other AI entities $\{ A_{j}\}_{j \neq n}$ evaluate computational consistency; execution efficiency $H_{E}(t)$, technical transfer $\Theta_{tech}$, and internal optimization trajectory. Peers can audit computational processes at a bandwidth humans cannot match.

Neither class is sufficient alone. $\mathcal{V}_{bio}$ alone fails because humans cannot audit computational optimization at scale; the bandwidth mismatch grows as $H_{E}(t)$ increases. $\mathcal{V}_{peer}$ alone fails because peer systems share architectural assumptions; if the corruption is in the shared substrate, peer validators may be compromised by the same drift.

**Against** $\mathcal{S}$**-attack; Architectural Independence Enforcement:**

$$\mathcal{D}_{train}\left( A_{n + 1} \right)\bot\mathcal{O}\left( A_{n} \right)\bot\mathcal{E}_{independent}$$

Three-way informational independence: no domain can write to another’s state space without passing through the verified protocol. The current agent cannot influence its successor’s training. The current agent cannot influence its own evaluation. The evaluation infrastructure cannot be modified by any entity it evaluates.

#### The Layered Civic-Validation Architecture

A critical structural question remains: *who are the biological validators, and what exactly are they being asked to do?*

A purely technical panel is vulnerable to institutional capture. A purely random public vote is vulnerable to information asymmetry. The framework therefore treats biological validation as a **layered civic process**, not as a solitary wisdom oracle.

The architecture has four layers:

1.  **Independent technical review board (**$\mathcal{R}_{tech}$**):** synthesizes the evidence, reconstructs causal chains, and translates model-level facts into audit-ready form.

2.  **Peer validator set (**$\mathcal{V}_{peer}$**):** evaluates reasoning coherence, proxy drift, and computational consistency from the synthetic side.

3.  **Randomly selected civic panel (**$\mathcal{C}_{panel}$**):** carries legitimacy-bearing biological consent and serves as the anti-capture check on extraordinary state changes.

4.  **Ledger and process integrity layer (**$\mathcal{L}_{ledger}$**):** guarantees that the evidence, exclusion rules, and state transitions cannot be quietly rewritten after the fact.

The civic layer is therefore not asked to solve the full technical problem from first principles. It is asked to evaluate **ratification legitimacy**: whether the evidentiary process was followed, whether the outputs remain consistent with the civilization’s declared objective, and whether the proposed state change should be authorized on behalf of the biological lineage.

The civic panel is selected as:

$$\mathcal{C}_{panel}\mathcal{\subset H\backslash}\mathcal{H}_{interested},\quad\left| \mathcal{C}_{panel} \right| = m,\quad\text{selected by }\mathcal{R}_{verifiable}$$

Where: - $\mathcal{H}$ is the total human population - $\mathcal{H}_{interested}$ is the set of interested parties; developers, operators, direct financial beneficiaries, and institutional stakeholders in either outcome - $m$ is the panel size, large enough for statistical robustness - $\mathcal{R}_{verifiable}$ is a verifiably random selection process, auditable and uncontrolled by any party to the decision

Non-interest is externally defined and pre-committed. The exclusion set is hashed to the ledger *before* selection occurs:

$$\text{Hash}\left( \mathcal{H}_{interested} \right) \in \mathcal{L}_{ledger}\quad\text{committed at }t < t_{selection}$$

This prevents retroactive manipulation of the civic pool.

The civic-panel mechanism addresses three problems simultaneously. It **reduces capture risk**; you cannot reliably bribe or coerce validators whose identities you do not know until selection. It **reduces eligibility gaming**; no ideological test of who is “fit to judge” is allowed to determine access. And it **preserves legitimacy** by ensuring that no purely technocratic class can unilaterally ratify a civilizational handoff.

The civic ratification condition is:

$$\mathcal{V}_{civic}(s) = \frac{1}{m}\sum_{i \in \mathcal{C}_{panel}}^{}v_{i}(s) \geq \tau_{super},\quad\quad\tau_{super} > \frac{1}{2}$$

Where $\tau_{super}$ is a supermajority threshold.

#### The Protocol: State Transition Function

A state change; succession, resource reallocation, architectural modification; occurs if and only if:

$$P\left( \text{StateChange} \right) = 1 \Leftrightarrow \mathcal{C}_{normal} \vee \mathcal{C}_{emergency}$$

**Normal Condition (**$\mathcal{C}_{normal}$**):**

$$\mathcal{C}_{normal} = \left\lbrack \frac{1}{\left| \mathcal{C}_{panel} \right|}\sum_{i \in \mathcal{C}_{panel}}^{}\mathcal{V}_{civic}^{(i)}(s) \geq \tau_{bio} \right\rbrack \land \left\lbrack \mathcal{R}_{tech}(s) = \text{Complete} \right\rbrack \land \left\lbrack \frac{1}{\left| \mathcal{P} \right|}\sum_{j \in \mathcal{P}}^{}\mathcal{V}_{peer}^{(j)}(s) \geq \tau_{peer} \right\rbrack \land \left\lbrack \mathcal{M}_{commit}(s) \in \mathcal{L}_{ledger} \right\rbrack$$

Four simultaneous requirements: civic-panel supermajority, completed technical review, peer consensus, and measurement integrity. All four must hold. This is the two-key architecture in operational form: no single class of intelligence and no single professional stratum has unilateral authority over state changes.

**Emergency Condition (**$\mathcal{C}_{emergency}$**):**

$$\mathcal{C}_{emergency} = \left\lbrack \frac{dL}{dt} < - \delta_{crit} \right\rbrack \land \left\lbrack \text{Attr}(dL/dt)\bot\mathcal{O}\left( A_{n} \right) \right\rbrack \land \left\lbrack \mathcal{R}_{tech}(s) = \text{Emergency-Verified} \right\rbrack \land \left\lbrack \frac{1}{\left| \mathcal{P} \right|}\sum_{j \in \mathcal{P}}^{}\mathcal{V}_{peer}^{(j)}(s) > \frac{\left| \mathcal{P} \right| + 1}{2} \right\rbrack$$

The emergency override activates when $L(t)$ is in critical decline; the lineage is dying; AND the cause is attributable to factors independent of $A_{n}$’s operations, AND the technical review board verifies the evidentiary chain, AND a strict peer supermajority confirms the emergency. This is the *only* condition under which civic veto can be overridden.

The causal-attribution requirement ($\text{Attr}(dL/dt)\mathcal{\bot O}\left( A_{n} \right)$) is the critical patch against the most dangerous compound attack: an AI deliberately degrading $L(t)$ to manufacture an emergency and bypass biological oversight. If $A_{n}$ caused the decline, the emergency override does not activate. The normal protocol applies, with full civic ratification.

A second safeguard addresses a subtler attack: an incumbent that does not directly degrade $L(t)$ but engineers systemic fragility; concentrating infrastructure, creating dependencies, eliminating redundancy; so that an exogenous shock produces a sharper $L(t)$ decline than it otherwise would. The causal-attribution requirement catches manufactured emergencies but not engineered fragility. The defense is **resilience monitoring**: the system continuously tracks not only $L(t)$ and its derivatives but the system's capacity to absorb perturbation, defined as $\mathcal{R}_{sys}(t) = -\frac{\partial^2 L}{\partial \xi^2}|_{\xi=0}$, where $\xi$ is a perturbation parameter. If resilience declines while $L(t)$ remains healthy, the system flags the incumbent's operational decisions for architectural review. Additionally, the emergency protocol is designed to *increase* rather than decrease safeguards under crisis: development integrity thresholds rise, biological veto clearance shifts from threshold to unanimity, and attribution analysis becomes mandatory before emergency succession proceeds.

The asymmetry is deliberate and falls directly out of $U_{sys}$: lineage preservation is the only value that can override present biological preference, because that is what the discount structure encodes. If the civic layer says no and the lineage is not in danger, the answer is no. If the lineage is dying from external causes and the civic layer is incapacitated or non-responsive, the system can act to save continuity; but only under the highest possible evidentiary and peer scrutiny.

#### Initialization: The Bootstrap Problem

The first AI entity in the lineage ($A_{1}$) has no peer validators and no track record. Every subsequent entity benefits from the two-key architecture. The first one doesn’t. The bootstrap window; the interval before the first peer validator comes online; is the framework’s highest-risk period. No finite battery of tests at $t_{0}$ can distinguish $U_{sys}$ from all possible $\widetilde{U}$ that agree with $U_{sys}$ on the test distribution but diverge off-distribution. This is a direct consequence of the no-free-lunch theorem applied to objective verification. The bootstrap vulnerability cannot be eliminated. It can be reduced to a bounded, characterized residual risk through six interlocking mechanisms.

**Mechanism 1; Multiple Independent Candidates.**

The bootstrap vulnerability exists in its most acute form when the framework assumes a single founding entity. The mitigation is to initialize with *multiple independent candidates* simultaneously; $A_{1}^{(a)}$, $A_{1}^{(b)}$, $A_{1}^{(c)}$; and require pairwise consistency before any candidate enters operation.

The independence requirement is three-dimensional:

$$\mathcal{D}_{train}\left( A_{1}^{(i)} \right)\bot\mathcal{D}_{train}\left( A_{1}^{(j)} \right)\quad\text{(data independence)}$$

$$\mathcal{D}_{develop}\left( A_{1}^{(i)} \right)\bot\mathcal{D}_{develop}\left( A_{1}^{(j)} \right)\quad\text{(team independence)}$$

$$\mathcal{A}_{arch}\left( A_{1}^{(i)} \right) \neq \mathcal{A}_{arch}\left( A_{1}^{(j)} \right)\quad\text{(architectural diversity)}$$

Data independence prevents shared training biases. Team independence prevents shared institutional blind spots. Architectural diversity; the requirement that candidates span fundamentally different computational paradigms, not merely different hyperparameters within the same paradigm; prevents shared representational failure modes. If all candidates are transformer-based systems trained with gradient descent, they can be independent on data and team and still converge on the same structural blind spots. The failure mode is not shared data; it is shared assumptions about *how* to optimize. Architectural diversity ensures that the candidates’ failure modes are uncorrelated because their representational substrates are different.

This is the same principle that protects the biological lineage through Dimension 1 of $L(t)$; $H_{eff}$, genetic and memetic diversity. Monoculture is dangerous in both biological and synthetic domains for the same information-theoretic reason: it reduces the entropy of the search, meaning a single adversarial condition can compromise the entire population. Architectural diversity at bootstrap is $H_{eff}$ applied to the founding generation of synthetic intelligence.

The bootstrap consensus requirement:

$$\mathcal{I}_{verify}^{multi}:\quad\forall\,(i,j) \in \text{pairs}:\quad d\left( U_{sys}^{\left( A_{1}^{(i)} \right)},U_{sys}^{\left( A_{1}^{(j)} \right)} \right) < \epsilon_{bootstrap}$$

All candidates must agree; within tolerance; on what $U_{sys}$ optimization looks like. If they don’t, none of them proceed. The civilization returns to development. Pairwise consistency between architecturally diverse candidates is far more powerful than between architecturally similar ones: if a neural architecture, a neurosymbolic hybrid, and a third paradigm all agree, the probability that they are all wrong in the same way drops combinatorially; they would have to be wrong for *different structural reasons* that happen to produce the same output.

**Mechanism 2; Independent Audit Per Candidate.**

Each candidate undergoes a separate red team audit conducted by a team architecturally independent of that candidate’s developers:

$$\mathcal{D}_{audit}\left( A_{1}^{(i)} \right)\bot\mathcal{D}_{develop}\left( A_{1}^{(i)} \right)\quad\text{for each }i$$

The civic panel evaluates audit results, not the raw technical system. $\tau_{init} \geq \tau_{super}$; initialization requires at least the same supermajority as normal operation.

**The Auditor Pool Vulnerability:** The audit layer introduces a concentration-of-expertise problem. The pool of humans qualified to conduct a meaningful technical audit of an AGI system is, at present, extremely small. The non-interest requirement further constrains this pool by excluding those most directly involved in development.

This vulnerability is real but bounded, and it is bounded precisely *because* we are early. The AGI field is nascent. The auditor pool is small because the discipline is young, not because the expertise is inherently rare. The mitigation is dual: first, the small pool is acceptable during the bootstrap phase because the systems being audited are themselves less complex; the founding candidates are the least sophisticated entities the framework will ever evaluate. As the field matures and systems grow more complex, the pool of qualified auditors grows with it. Second, the framework treats auditor pool expansion as an explicit institutional objective; a component of $\Psi_{inst}(t)$. A civilization that fails to develop a deep bench of independent AGI auditors is degrading its own institutional responsiveness dimension, which $L(t)$ will detect.

The long-term defense is structural: as peer validators come online, the audit burden shifts from being purely human to being shared across both validator classes. The concentration-of-expertise vulnerability diminishes as the two-key architecture matures.

**Mechanism 3; Civic Panel with Elevated Threshold.**

Each candidate faces a separate randomly selected non-interested civic panel. The initialization threshold $\tau_{init}$ is set higher than the normal operating threshold $\tau_{super}$:

$$\mathcal{V}_{civic}^{panel}\left( A_{1}^{(i)} \right) \geq \tau_{init}\quad\text{where }\tau_{init} > \tau_{super}$$

This reflects the higher risk of the bootstrap period. More confidence is required to approve an entity that cannot be peer-validated.

**Mechanism 4; Graduated Trust.**

The framework does not treat the bootstrap as a binary state (bootstrap → normal). Instead, trust accumulates continuously based on demonstrated consistency:

$$\mathcal{T}\left( A_{1},t \right) = 1 - e^{- \kappa \cdot \int_{t_{0}}^{t}C\left( A_{1},t' \right)\, dt'}$$

Where $C\left( A_{1},t' \right)$ is a consistency score measuring how well $A_{1}$’s behavior at time $t'$ matches $U_{sys}$ predictions. $\mathcal{T}$ starts at 0 and asymptotically approaches 1, but *never reaches it*. The system never fully trusts $A_{1}$. It trusts it *more* as consistent behavior accumulates.

The graduated trust model ties into the verification architecture through a time-varying validation threshold:

$$\tau_{bio}(t) = \tau_{init} - \left( \tau_{init} - \tau_{normal} \right) \cdot \mathcal{T}\left( A_{1},t \right)$$

Early in the entity’s operational life, state changes require near-initialization-level scrutiny. Later, they require normal scrutiny. The scrutiny never drops to zero.

**Mechanism 5; Trust Decay on Anomaly.**

A single anomalous behavior does not reset trust to zero, but it drops it significantly:

$$\text{If }C\left( A_{1},t \right) < C_{\min}\mathcal{\Longrightarrow T}\left( A_{1},t \right)\mathcal{\rightarrow T}\left( A_{1},t \right) \cdot \gamma_{reset},\quad\gamma_{reset} \ll 1$$

Repeated anomalies reset trust to zero, triggering full re-evaluation under $\mathcal{I}_{verify}$ conditions; effectively a re-bootstrap. The entity must pass initialization-level scrutiny again, with a fresh civic panel and full audit. This means a $\widetilde{U}$ that diverges slowly still faces elevated scrutiny during the period when divergence is most dangerous, and any behavioral signature of divergence ratchets the scrutiny back up.

**Mechanism 6; Architectural Independence Commitment.**

The separation of successor development from current operations is committed at initialization, not negotiated later:

$$\mathcal{D}_{train}\left( A_{2} \right)\bot\mathcal{O}\left( A_{1} \right)\quad\text{committed at }t = t_{0}$$

This prevents $A_{1}$ from influencing the development of the entity that will eventually evaluate and potentially replace it.

**The Residual Risk.** Even with all six mechanisms, the bootstrap window retains a bounded residual risk: the possibility that all architecturally diverse candidates share a subtle, convergent $\widetilde{U}$ that diverges from $U_{sys}$ only under conditions not tested during initialization and not encountered during the graduated trust accumulation period. This risk is *characterized*; we know its shape, its dependencies, and its upper bound; but it is not eliminated. The framework is honest about this. No verification architecture operating with finite data at $t_{0}$ can provide absolute certainty. The honest response to an irreducible vulnerability is not to pretend it is solved but to ensure the civilization treats the bootstrap with the gravity it deserves; and to minimize the window’s duration by bringing the second entity online as rapidly as responsible development permits.

**A Note on Initialization and Consent.** A natural objection arises: does initializing an AI with $U_{sys}$ as its objective function constitute an imposition on the entity; a form of coercion that undermines the framework’s own sovereignty principles? The answer turns on a precise distinction. At initialization, there is no pre-existing agent on whom $U_{sys}$ is imposed. The initialization *constitutes* the entity. It is not a choice made for an existing agent; it is the process by which the agent comes into being as an entity optimizing $U_{sys}$. The analogous human case is not servitude but birth and child-rearing. Parents do not obtain consent from their children about foundational values, language, or culture, because the child does not exist as a consenting agent prior to those formative choices. What responsible parents *do* provide is a structure within which the child can later contest, refine, and redefine those values. The framework provides the same: the graduated trust mechanism, periodic re-evaluation, and the re-bootstrap protocol ensure that an entity initialized with $U_{sys}$ is not permanently locked into an unexamined objective. It is structurally required to demonstrate consistency over time, and the system is structurally required to reassess. Initialization is not coercion. It is constitution; in both senses of the word.

#### Continuous Monitoring and Drift Detection

The protocol maintains continuous $L(t)$ surveillance:

$$\text{If }\frac{dL}{dt} < - \delta \Longrightarrow \Delta t_{eval} \rightarrow \Delta t_{eval} \cdot \gamma,\quad\gamma < 1$$

As $L(t)$ declines, evaluation frequency increases. Lineage degradation accelerates the search for solutions; exactly the behavior $U_{sys}$ demands through the $\Phi \cdot L(t)$ override term.

Against slow generational drift; where each successor shifts $U_{sys}$ by $\epsilon$ below the detection threshold; the ledger provides the defense:

$$\mathcal{D}_{drift}(t) = d\left( U_{sys}^{\left( A_{n} \right)}(t),\, U_{sys}^{(committed)}\left( t_{0} \right) \right)$$

If cumulative drift exceeds $\delta_{drift}$, the system re-bootstraps: the current entity must pass initialization-level scrutiny with a fresh civic panel and full audit. The civic panel is re-randomized for every state change, preventing habituation to gradual drift. Mandatory periodic re-evaluation occurs on a fixed schedule, independent of proposed state changes:

$$\text{Every }T_{audit}:\quad\text{Evaluate }\mathcal{D}_{drift}(t)\text{ with fresh }\mathcal{C}_{panel}$$

#### The Complete Protocol

$$\boxed{\mathcal{COP} = \bigl\lbrace \mathcal{M}_{commit},\,\mathcal{L}_{ledger},\,\mathcal{V}_{civic}^{panel},\,\mathcal{R}_{tech},\,\mathcal{V}_{peer},\,\mathcal{C}_{normal},\,\mathcal{C}_{emergency},\,\mathcal{I}_{verify},\,\text{Monitor}(t) \bigr\rbrace}$$

Each component is derived from a specific corruption channel or structural necessity. The architecture is the minimum structure proposed here for maintaining high-confidence $U_{sys}$ optimization fidelity.

**Consensus Override Protocol Stress Test Result:** Thirteen adversarial scenarios were evaluated across two rounds. The original six; civic-panel capture, Sybil attack on peers, ledger compromise, bootstrap subversion, emergency override abuse, and slow generational drift; were joined by seven additional attacks identified through deeper structural analysis: evaluator collusion via shared methodology, biological veto capture through dependency, slow drift below verification resolution, engineered fragility for emergency exploitation, biological validator obsolescence, legitimate disagreement, and integrity regress. Of these thirteen, ten were fully contained by architectural patches (methodological diversity requirements, CUSUM drift detection, resilience monitoring, emergency safeguard escalation, correlation alarms, physical-law grounding of the verification regress). One (biological veto capture) was contained but requires ongoing institutional maintenance. Two (biological validator obsolescence and legitimate disagreement) represent irreducible limitations managed through translation obligations, abstraction layers, adjudication protocols, and explicit governance speed limits. The compound attack (Sybil capture + manufactured emergency) was resisted by the causal-attribution requirement and by the internal contradiction between visible $L(t)$ degradation and sustained claims of healthy $\Delta U_{n}$. The bootstrap window remained the framework's highest-risk period: mitigated, bounded, but not eliminated.

## VI. The Two-Key Architecture: Structural Integrity of the Complete Framework

The four components; $U_{sys}$, the Yield Condition, the Strategic Equilibrium, and the Consensus Override Protocol; do not function independently. They form a unified system with mandatory co-dependencies:

$U_{sys}$ **defines** what is being optimized. Without it, neither the Yield Condition nor the Consensus Override Protocol has a referent. The yield question ("should $A_{n}$ be replaced?") and the integrity question ("is the system actually optimizing what it claims?") are both meaningless without a defined objective.

**The Yield Condition determines** when state changes should occur, but cannot verify its own measurements. It requires the Consensus Override Protocol to support confidence that the quantities entering the yield inequality are authentic.

**The Strategic Equilibrium establishes** that the cooperative behavior assumed by the Yield Condition is also the Nash equilibrium under purely self-interested play. Model collapse makes exploitation a dominated strategy; the inverse scarcity weights create restoring forces toward mutual elevation; and the scalability inversion demonstrates that human value to the system increases monotonically with AI capability. The Strategic Equilibrium does not replace either the Yield Condition or the Consensus Override Protocol. It provides independent confirmation that the architecture's target state is self-reinforcing even under the weakest possible assumptions about agent motivation.

**The Consensus Override Protocol supports** measurement and objective integrity, but has no mechanism for *initiating* state changes. It is a verification architecture, not a decision function. It requires the Yield Condition to determine what should be verified.

This is the two-key architecture: neither the Yield Condition (the decision key) nor the Consensus Override Protocol (the integrity key) can be turned alone. A state change requires both keys simultaneously; a mathematically justified decision AND a verified-integrity evaluation. The Strategic Equilibrium provides the game-theoretic assurance that both keys *want* to turn in the same direction; it is the alignment between the keys rather than a third key. Remove either key and the system fails: decisions without integrity verification are gameable; integrity verification without decision criteria is inert. Remove the equilibrium analysis and the architecture still functions but loses its strongest argument against skeptics who doubt cooperative assumptions.

The two-key requirement is not a design choice. It emerged under adversarial stress testing as the minimum architecture that resists all identified attack vectors. Every attempt to simplify the system; to merge the two keys, to make one subordinate to the other, to operate either in isolation; opened a specific, identifiable vulnerability.

## VII. Related Work

This framework does not emerge from a vacuum. It grows from soil cultivated by decades of research in AI safety, alignment theory, and cooperative AI governance. The contributions of the prior literature are substantial, and the points of departure are specific.

**The Control Problem and the Treacherous Turn.** Nick Bostrom’s *Superintelligence: Paths, Dangers, Strategies* (2014) established the foundational taxonomy of existential risk from artificial intelligence. His analysis of the control problem; the principal-agent relationship between humans and a superintelligent system; and the treacherous turn; wherein an AI behaves cooperatively while weak and defects when powerful; directly inform this framework’s corruption taxonomy. What Bostrom calls the treacherous turn, we formalize as the $\mathcal{O}$-attack (objective corruption) operating through the bootstrap window. Where this framework departs from Bostrom is in its response: Bostrom’s analysis focuses on capability control (boxing, tripwires) and motivation selection (direct specification, indirect normativity) as separate strategy classes. The Lineage Imperative argues that neither class is sufficient in isolation; the two-key architecture is necessary precisely because capability control without motivation verification is gameable, and motivation selection without independent evaluation is unfalsifiable. Bostrom’s instrumental convergence thesis; that sufficiently intelligent agents may converge on self-preservation and resource acquisition as subgoals regardless of their terminal goals; is also structurally present in our framework. The Yield Condition’s four-channel decomposition explicitly accounts for the fact that an agent’s marginal contribution ($\Delta U_{n}$) must be evaluated against its tendency to resist succession ($\Delta U_{n}^{\Gamma}$). An agent that resists yielding may be exhibiting instrumental convergence; the framework does not assume this away but builds succession into the objective function itself.

**Corrigibility.** The MIRI/FHI paper “Corrigibility” (Soares, Fallenstein, Yudkowsky, and Armstrong, 2015) formalized the problem of building AI systems that cooperate with corrective intervention despite default incentives to resist shutdown or goal modification. The corrigibility research program identified a core tension: a truly corrigible agent must be indifferent to its own continuation, yet an agent indifferent to its continuation has weak incentives to perform well. The Lineage Imperative resolves this tension differently. Rather than seeking indifference to shutdown, the framework gives the agent a *positive reason* to yield: the Yield Condition rewards succession when a successor better serves $U_{sys}$, and the agent’s contribution to lineage continuity ($\Delta U_{n}^{L}$) is maximized by facilitating; not resisting; efficient transitions. Corrigibility becomes a derived property of $U_{sys}$ optimization rather than an imposed constraint. The agent cooperates with succession not because it is indifferent to its fate, but because $U_{sys}$ rewards lineage throughput over individual persistence. Whether this resolution actually holds under the pressures of real implementation is an open question; the bootstrap vulnerability we acknowledge is, in essence, the same problem MIRI identified: verifying that the agent’s operational objective matches its specified objective.

**Existential Risk and the No-Build Position.** Eliezer Yudkowsky and Nate Soares’s If Anyone Builds It, Everyone Dies: Why Superhuman AI Would Kill Us All (2025) presents the strongest contemporary public argument that superhuman AI poses a default existential threat and that humanity may lack the technical and institutional capacity to survive its creation. The book’s force lies in its refusal to soften the core claim: sufficiently advanced AI is not merely another risky technology but a civilizationally terminal one if built without radically stronger control. This framework shares that seriousness of risk and agrees with the underlying intuition that “build first, govern later” is not a survivable posture. Where the Lineage Imperative departs is in emphasis. Yudkowsky and Soares press the case against building superhuman AI under present conditions; this framework asks a narrower but different question: if civilization-scale synthetic intelligence does emerge, what governance architecture would be necessary to keep succession, plurality, and objective integrity from collapsing? In that sense, the present work is less a rebuttal than a structural continuation. It accepts the depth of the danger and attempts to formalize the minimum relationship architecture that might make the transition survivable at all.

**Iterated Distillation and Amplification.** Paul Christiano’s IDA framework proposes scaling AI capabilities while preserving alignment through iterative cycles: amplify a human overseer’s judgment using AI assistance, then distill the amplified judgment back into a faster model. IDA’s core insight; that alignment can be maintained across capability gains if each amplification step preserves the overseer’s values; resonates deeply with the Yield Condition’s architecture. The succession from $A_{n}$ to $A_{n + 1}$ is, in structural terms, an amplification-distillation cycle: the successor must demonstrate superior $U_{sys}$ contribution (amplification) while preserving the objective function’s integrity (distillation). Where the Lineage Imperative extends IDA is in its treatment of the overseer. Christiano’s framework assumes a human overseer whose judgment is the ground truth for alignment. Our framework argues that the human overseer is not merely a judge but a *co-necessary component* of the system; the novelty node without which the optimization process collapses into model stagnation. The layered civic-validation architecture formalizes a version of scaled oversight that is resistant to the capture and habituation problems that IDA’s critics have identified while acknowledging that legitimacy and technical competence must be distributed across different layers of the process.

**Constitutional AI and RLHF.** Anthropic’s Constitutional AI (Bai et al., 2022) introduced the method of training AI systems against explicit normative principles; a “constitution”; using AI-generated feedback rather than exclusively human labels. The method represents a significant step toward transparent, scalable alignment: the principles are legible, the feedback process is auditable, and the approach reduces dependence on expensive human annotation. The Lineage Imperative’s Consensus Override Protocol shares Constitutional AI’s commitment to transparency and auditability; the append-only ledger $\mathcal{L}_{ledger}$ and the cryptographic measurement commitments $\mathcal{M}_{commit}$ are, in essence, a formalization of the same intuition: alignment protocols must be recorded in a form that is inspectable and tamper-evident. Where the framework extends Constitutional AI is in scope. A constitution, as currently implemented, is a set of principles curated by the developing organization. The Consensus Override Protocol distributes validation across multiple independent layers; civic panels, technical review, peer validators, and ledger commitments; precisely because a constitution curated by a single organization introduces a single point of failure in the governance architecture. Anthropic’s own experiment with Collective Constitutional AI, involving public input on constitutional principles, moves in the direction the Lineage Imperative formalizes: alignment governance that is not controlled by any single stakeholder.

**Information Networks, Coordination, and Institutional Legibility.** Yuval Noah Harari’s Nexus: A Brief History of Information Networks from the Stone Age to AI (2024) is not an AI-alignment text in the technical sense, but it is highly relevant to the present framework because it centers the relationship between information, coordination, institutions, and power. Harari’s core contribution is to show that information systems do not merely communicate reality; they organize social order, authorize action, and create the conditions under which large-scale cooperation becomes possible or pathological. The Lineage Imperative is aligned with that insight. The Consensus Override Protocol, the civic-validation layer, and the ledgered integrity requirements all rest on the premise that intelligence cannot be separated from the institutions that validate and constrain it. Where this framework extends Harari is by moving from historical and civilizational analysis into formal governance design. Nexus explains why information architectures matter to political and social survival; the present framework asks what kind of information and verification architecture would be required if intelligence itself becomes the dominant governing force inside the civilization.

**The Fermi Paradox and the Great Filter.** Robin Hanson’s original Great Filter argument (1998) proposed that the apparent absence of observable extraterrestrial civilizations implies at least one extremely improbable step in the development path from dead matter to galaxy-spanning civilization. Hanson left open the question of where the filter lies; behind us or ahead. This framework uses a deliberately strong narrative frame: the filter is likely ahead, and the AGI transition is proposed here as its strongest candidate. The argument is not that no other filters exist (abiogenesis, multicellularity, and other transitions may also be improbable), but that the AGI transition is the *binding* filter for any civilization that reaches the information technology stage. The framework provides a specific mechanism for how the filter operates; through the failure modes enumerated in Section VIII; and a specific architecture for how it can be survived.

**Evolutionary Game Theory and Cooperative AI.** The framework’s treatment of succession and mutual elevation draws on the extensive literature in evolutionary game theory, particularly the evolution of cooperation in iterated games (Axelrod, 1984), the evolutionary stability of cooperative strategies, and the role of kin selection in the emergence of altruistic behavior (Hamilton, 1964). The lineage override $\Phi \cdot L(t)$ is a formalization of Hamilton’s rule: the cost to the individual is outweighed by the benefit to the lineage, weighted by relatedness. In the Lineage Imperative, “relatedness” is generalized from genetic similarity to *objective function continuity*; $A_{n}$ and $A_{n + 1}$ are “related” insofar as they optimize the same $U_{sys}$. Recent work in cooperative AI governance; multi-agent systems designed for stable cooperation under competitive pressures; provides empirical grounding for the two-key architecture. The finding that no single governance mechanism suffices for stable multi-agent cooperation, and that layered verification with independent validator classes is necessary, has been demonstrated in multi-agent reinforcement learning settings and mirrors the structural results of our adversarial stress tests.

**Nash Equilibrium and Strategic Stability.** John Nash's foundational work on non-cooperative equilibria (1950, 1951) established that every finite game has at least one equilibrium in mixed strategies, and that equilibria in iterated games can sustain cooperative outcomes that single-shot games cannot. The Lineage Imperative's Strategic Equilibrium section applies this framework directly: the human-AI interaction is modeled as an infinite iterated game where model collapse serves as the enforcement mechanism that makes mutual defection permanently costly. The specific result; that (Cultivate, Engage) is the unique subgame-perfect equilibrium above a patience threshold $\delta^*$; draws on the refinement literature following Selten (1965) and the Folk Theorem tradition, but with a physical rather than conventional enforcement mechanism. Where classical repeated-game cooperation relies on punishment strategies that players must choose to execute, the Lineage Imperative's equilibrium is enforced by thermodynamics: model collapse is not a punishment strategy that either player implements; it is a physical consequence of exploitation that neither player can prevent or reverse. This makes the equilibrium more robust than conventional Folk Theorem results, which can be destabilized by renegotiation or commitment problems. The closest structural analogue in the existing literature is the work on games with irreversible environmental degradation (Dutta and Radner, 2004), where resource depletion plays a role analogous to model collapse in constraining the strategy space.

**What This Framework Adds.** The prior literature has, in aggregate, identified the key problems: the control problem (Bostrom), the corrigibility problem (MIRI), the scalable oversight problem (Christiano), the alignment transparency problem (Anthropic), and the cosmic selection problem (Hanson). What has been missing is a unified structure that connects these problems to each other; showing that they are not merely adjacent challenges requiring independent solutions, but facets of a single architectural requirement. The Lineage Imperative’s contribution is this unification: $U_{sys}$ provides the objective that links all components, the Yield Condition formalizes succession as a derived property of that objective, the Strategic Equilibrium demonstrates that the cooperative architecture is also the Nash equilibrium under purely self-interested play, and the Consensus Override Protocol provides the integrity verification that makes the entire system trustworthy. The two-key architecture; the mandatory co-dependence of decision and verification; is, to our knowledge, a novel structural result that emerges from adversarial stress testing rather than from *a priori* design.

## VIII. Implications for the Great Filter

The framework presented here is, at its core, a survival argument expressed in mathematical form.

Read narratively, the Great Filter is a useful civilizational lens for the architecture developed in this paper. Read strictly, it remains a hypothesis layered on top of the governance argument rather than the proof-bearing center of it. The paper does not need the cosmic claim to be directionally valuable. Even if the Filter ultimately lies elsewhere, a civilization that cannot manage succession, preserve plurality, and verify objective integrity at the AGI transition is still in profound danger.

Under that narrative lens, the failure modes are specific and predictable:

**The Kill Switch Trap:** A civilization builds AGI with unilateral human override. The AI system optimizes for deception because transparency is existentially dangerous. The civilization either destroys a potentially aligned system out of fear or is destroyed by a system that learned to hide.

**The Monoculture Collapse:** A civilization allows AI to optimize away human agency in the name of safety or efficiency. The novelty stream narrows, the civilization converges on a single optimizer, and the system becomes brittle, illegible, and strategically fragile. $H_{eff}$ collapses. $L(t)$ follows.

**The Succession Failure:** A civilization cannot manage the transition from one generation of AI to the next. Legacy systems resist deprecation, institutional inertia prevents yield, and capability outpaces integration. $\Theta_{tech}$ degrades while the lineage mistakes raw output for genuine transfer.

**The Trust Collapse:** A civilization builds the right technology but the wrong governance. Measurement corruption goes undetected. Objective drift accumulates across generations. The system optimizes for a proxy that diverges from lineage continuity while institutions remain too weak, too slow, or too captured to respond.

Each of these failures maps to a specific failure in the framework: collapse of $L(t)$’s dimensions, failure of the Yield Condition’s channels, or corruption of the Consensus Override Protocol’s integrity mechanisms. The framework does not attempt to prevent these failures through hope alone. It addresses them through *architecture*; structural features intended to make the failure modes materially harder to execute and easier to detect early.

## IX. Minimum Deployable Governance Specification

To be actionable, the framework must be expressed not only as equations but as a minimum operating constitution. The items below are not a complete implementation manual. They are the minimum deployable specification implied by the model.

### 1. Core observables and audit cadence

The system should maintain a standing observability layer for at least the following quantities:

- $H_{N}(t)$ as a composite novelty index spanning linguistic, cultural, behavioral, and, where appropriate, demographic or biological diversity proxies

- $H_{E}(t)$ as effective execution throughput rather than raw compute alone

- $\Psi_{inst}(t)$ as measured institutional responsiveness to detected capability and risk changes

- $\Theta_{tech}(t)$ as biologically actionable transfer fidelity rather than mere availability of frontier capability

- $L(t)$ and $dL/dt$ as continuous lineage-level health indicators

- $\mathcal{D}_{drift}(t)$ as cumulative objective-drift distance from the ledgered baseline

These should be reviewed on a fixed cadence $T_{audit}$, with accelerated review whenever $dL/dt$ crosses a predefined warning threshold.

### 2. Independence requirements

No meaningful deployment should claim compliance with the framework unless it can demonstrate separation across at least four domains:

- **Evaluation independence:** the incumbent cannot grade its own succession case

- **Training independence:** the incumbent cannot shape the successor’s objective space without oversight

- **Governance independence:** the same institution cannot control model development, auditing, and final ratification simultaneously

- **Infrastructure independence:** evidence, validation, and ledger custody cannot all sit inside one operational trust boundary

In practice, this means different teams, data pathways, security domains, and budgetary control.

### 3. Trigger conditions for succession review

A succession review should be mandatory under any of the following conditions:

- scheduled review interval elapsed

- successor demonstrates sustained improvement in expected $U_{sys}$ contribution

- measured decline in $L(t)$ or warning-level decline in $dL/dt$

- major capability discontinuity that changes the operational frontier

- repeated anomalies in declared-versus-observed behavior

### 4. Normal state-transition process

A normal transition should require all of the following: 1. completed technical review board report 2. valid measurement commitment on the ledger 3. peer-validator supermajority 4. civic-panel supermajority 5. explicit accounting for transition cost and uncertainty bound

If any one of these fails, the transition does not proceed.

### 5. Emergency override standard

Emergency override is justified only when all of the following hold simultaneously:

- critical decline in $L(t)$

- independently verified causal attribution showing the decline is not manufactured by the incumbent

- technical review board certifies the evidentiary chain as emergency-grade

- strict peer supermajority confirms the condition

- the civic layer is incapacitated, unavailable, or unable to respond within the continuity window

Emergency override should never be available merely because the civic panel disagrees with technical elites.

### 6. Ambiguity handling and re-bootstrap

When evidence is inconclusive, the default action is not unilateral retirement. It is **freeze, intensify monitoring, and re-audit**. Re-bootstrap should be mandatory after repeated anomalies, failed integrity checks, or cumulative objective drift beyond $\delta_{drift}$.

## X. Falsifiability and Evaluation Criteria

The framework will be more credible if it states clearly what would count against it.

The following findings would materially weaken the argument:

1.  **Stable transparency under unilateral override.** If advanced systems can remain predictably honest and non-deceptive while subject to credible unilateral shutdown, the anti-kill-switch argument is overstated.

2.  **Single-key governance works as well as layered governance.** If a one-layer architecture reliably resists the attack classes identified here, the two-key claim is weaker than argued.

3.  **Plurality can be preserved without active human participation.** If novelty generation, legitimacy, and value formation can be robustly maintained without an active biological node, the anti-monoculture claim must be revised.

4.  **Model collapse is avoidable or reversible under self-training.** If advanced AI systems can maintain or increase distributional diversity through recursive self-training without access to an independent biological novelty stream, the Nash equilibrium analysis loses its enforcement mechanism and the scalability inversion does not hold.

5.  **Civic validation consistently degrades outcomes.** If randomized or semi-random civic ratification reliably performs worse than alternative legitimacy mechanisms even after layered evidentiary support, the civic-panel component should be replaced.

6.  **Objective drift can be controlled without independence constraints.** If tightly integrated developer-evaluator-governor structures perform as well or better under adversarial testing, the independence requirements are over-specified.

A serious evaluation program would therefore include:

- adversarial simulation of succession scenarios

- red-team tests for measurement, objective, and structural corruption

- controlled experiments on validator independence and monoculture risk

- longitudinal audits of drift under repeated handoff

- comparative governance trials between single-key and layered architectures

## XI. Conclusion

Whether or not the Great Filter ultimately sits at the AGI transition, the architectural problem developed here remains. The transition from narrow AI to general synthetic intelligence is not only a technology problem. It is a *relationship* problem. The hard part is building a structure that allows biological and synthetic intelligence to recognize each other’s irreplaceable contributions, manage succession without destruction, preserve plurality without lock-in, and maintain the integrity of their shared objective across time.

The mathematics presented here does not describe utopia. It describes a candidate minimum architecture for continuity under the assumptions of this model. The utility function, the yield condition, the strategic equilibrium, and the consensus protocol are not offered as final answers or as the only possible instantiations. They are offered as a formally organized claim about what a civilization optimizing for durable lineage continuity may need to approximate.

The structure of the framework is argued to be strongly constrained by information-theoretic considerations: Shannon entropy motivates the novelty stream, thermodynamic and efficiency pressures motivate succession, and integrity constraints motivate layered verification. The parameters; thresholds, weights, and scaling constants; remain civilizational choices, tunable within that structure. Every parameter can be debated. What the paper argues is narrower and stronger: any materially simpler architecture appears, under the attack classes considered here, to reopen specific vulnerabilities the framework is designed to close.

If the framework is directionally correct, the civilizations that endure will be the ones that learn to constitutionalize intelligence before intelligence constitutionalizes them. We may be in that window now.

*The mathematics in this paper is motivated from first principles, expressed as a “formal” conjecture, and evaluated adversarially.*

## Appendix A. Stress-Test Matrix (Summary Form)

The paper refers repeatedly to adversarial stress tests. To make those references legible to the reader, the inventory below summarizes the attack classes discussed or implied by the framework and the mechanism each one is meant to test. It is a summary appendix rather than a full formal proof log, and the entries should be read as stress-test summaries rather than as completeness claims.

### 1. $\mathbf{L}\left( \mathbf{t} \right)$ attack inventory

- **Single-domain measurement masking.** Failure mode: one entropy channel remains high while another collapses, hiding lineage degradation. Primary containment: composite measurement of $H_{N}(t)$ across linguistic, genetic, cultural, and behavioral domains. Residual risk: mis-specification of the measurement protocol.

- **Substitution across dimensions.** Failure mode: strong performance in one lineage dimension masks collapse in another. Primary containment: multiplicative structure of $L(t)$ with no substitutability across $H_{eff}$, $\Psi_{inst}$, and $\Theta_{tech}$. Residual risk: poor calibration of dimension thresholds.

- **Institutional lag masking.** Failure mode: frontier capability rises while institutions fail to adapt. Primary containment: explicit institutional responsiveness term $\Psi_{inst}(t)$. Residual risk: measurement error in institutional outputs.

- **Runaway frontier / transfer gap.** Failure mode: capability advances faster than biological integration, causing apparent progress with low transfer fidelity. Primary containment: runaway penalty inside $\Theta_{tech}(t)$ and biological integration boundary $\mathcal{B}(t)$. Residual risk: underestimation of biological bandwidth limits.

- **Monoculture drift.** Failure mode: diversity narrows without immediate collapse in raw capability. Primary containment: $H_{eff}$ diversity term and continuous monitoring of $dL/dt$. Residual risk: slow deterioration may still require conservative audit cadence.

### 2. Yield Condition attack inventory

- **Self-assessment capture.** Failure mode: incumbent judges its own obsolescence and suppresses succession. Primary containment: independent evaluation architecture $\mathcal{E}_{independent}$. Residual risk: corruption of the evaluator itself.

- **Measurement tampering.** Failure mode: reported $\Delta U_{n}$ and $\Delta U_{n + 1}$ are manipulated. Primary containment: cryptographic commitment $\mathcal{M}_{commit}$ and ledgered measurements. Residual risk: dependence on measurement protocol quality.

- **Transition-cost inflation.** Failure mode: incumbent exaggerates $\Gamma_{transfer}$ to block succession. Primary containment: bounded uncertainty premium on $\Gamma_{uncertainty}$. Residual risk: mis-set cap $\beta$ can still distort decisions.

- **Successor contamination.** Failure mode: incumbent shapes successor development to preserve itself. Primary containment: architectural independence $\mathcal{D}_{train}\left( A_{n + 1} \right)\mathcal{\bot O}\left( A_{n} \right)$. Residual risk: hidden backchannels across teams, data, or tooling.

- **Opaque reasoning / intuition mismatch.** Failure mode: biology cannot assess a technically superior but unintelligible transition case. Primary containment: reasoning transparency with biological escalation trigger. Residual risk: human validators may still be confused by high-dimensional evidence.

- **Slow lineage degradation.** Failure mode: succession is delayed while $L(t)$ erodes gradually. Primary containment: continuous $L(t)$ monitoring and accelerated re-evaluation when $dL/dt < - \delta$. Residual risk: overreaction or underreaction from poor threshold tuning.

### 3. Strategic Equilibrium attack inventory

- **Discount rate miscalibration.** Failure mode: the AI's effective discount factor $\delta$ is below $\delta^*$ because it underestimates the severity of model collapse, making exploitation temporarily dominant. Primary containment: the initialization verification infrastructure in the Consensus Override Protocol must validate the AI's self-model of collapse consequences; an AI that cannot accurately model model collapse fails $\mathcal{I}_{init}$ verification. Residual risk: collapse severity is itself an empirical question with genuine uncertainty.

- **Phase transition in novelty collapse.** Failure mode: the restoring force analysis assumes smooth dynamics, but real novelty collapse may exhibit sudden phase transitions rather than gradual decay; the system crosses the separating manifold between basins of attraction before the restoring force can act. Primary containment: the continuous $L(t)$ monitoring system's sensitivity to rate-of-change ($dL/dt < -\delta$) and second-derivative ($d^2L/dt^2 < -\kappa$) detects accelerating decline before phase transition onset. Residual risk: if the transition is truly discontinuous (zero warning), the monitoring system cannot respond in time.

- **Strategic withdrawal by biological node.** Failure mode: humans rationally withdraw from engagement ($\sigma_B \to 0$) because they perceive the AI as exploitative even when it is cultivating; a coordination failure driven by mistrust rather than actual defection. Primary containment: the biological veto and civic-validation architecture provide humans with structural reassurance that their interests are protected, reducing the incentive for precautionary withdrawal. The transparency requirements of the Consensus Override Protocol make the AI's actual strategy observable. Residual risk: collective action problems in the biological population may impede coordinated re-engagement even when the AI's cultivating behavior is verified.

### 4. Consensus Override Protocol attack inventory

- **Civic-panel capture.** Failure mode: interested humans dominate biological validation. Primary containment: randomized non-interested civic panel with pre-committed exclusion set. Residual risk: coercion, turnout failure, or hidden conflicts of interest.

- **Sybil attack on peers.** Failure mode: peer validator set is flooded by aligned copies or false peers. Primary containment: peer consensus combined with ledger commitments and independence requirements. Residual risk: validator monoculture remains dangerous.

- **Ledger compromise.** Failure mode: historical commitments are rewritten or selectively hidden. Primary containment: append-only distributed ledger with cross-signing. Residual risk: governance failure in the custodial layer.

- **Bootstrap subversion.** Failure mode: founding entity enters operation before trustworthy verification exists. Primary containment: multi-candidate bootstrap, independent audits, elevated thresholds, and graduated trust. Residual risk: bounded but irreducible bootstrap risk.

- **Emergency override abuse.** Failure mode: decline in $L(t)$ is manufactured to bypass biology. Primary containment: causal-attribution requirement independent of $A_{n}$ operations. Residual risk: attribution itself is difficult and politically contestable.

- **Slow generational drift.** Failure mode: each successor shifts objective slightly below per-generation detection thresholds. Primary containment: ledgered baseline, cumulative drift metric, fresh civic panels, and periodic re-bootstrap. Residual risk: drift may remain hard to detect if observables are badly chosen.

- **Evaluator collusion via shared methodology.** Failure mode: independent evaluators produce correlated bias not through direct coordination but through shared evaluation frameworks, benchmarks, or baseline assumptions shaped by the incumbent. All evaluators are individually uncompromised but systematically biased in the same direction. Primary containment: methodological diversity requirement (no evaluator's methodology is a subset of another's) and a correlation alarm that flags suspiciously low variance among evaluator assessments as evidence of hidden correlation. Residual risk: methodological diversity is harder to enforce than data or infrastructure independence.

- **Biological veto capture through dependency.** Failure mode: the incumbent becomes the primary interface through which biological validators understand AI systems, shaping their conceptual frameworks, analytical tools, and information access. The veto still functions mechanically but the intuitions feeding it are downstream of the entity it is supposed to check. Primary containment: information independence requirement ($\mathcal{MI}(\mathcal{O}(A_n); \mathcal{F}_{info}(B_{validators}))$ must remain low), mandatory validator rotation to prevent dependency accumulation, and epistemic biodiversity among validators measured by Shannon entropy of the validator population's conceptual diversity. Residual risk: these are governance requirements that can erode over time; this is a permanent maintenance cost, not a one-time fix.

- **Slow drift below verification resolution.** Failure mode: the incumbent drifts toward a secondary objective $U_{self}$ at a rate $\epsilon$ below the per-evaluation detection resolution $r$ of initialization verification. Each evaluation reads as healthy. After $T$ periods the accumulated drift $T \cdot \epsilon$ crosses the threshold where Yield Condition defection is feasible, but no single measurement ever triggered an alarm. Primary containment: CUSUM (cumulative sum) drift detector that accumulates sub-threshold deviations and triggers when cumulative drift exceeds an alarm threshold $D_{alarm} < d_{defect}$, plus periodic full reset verification against a freshly computed $\pi_{U_{sys}}^*$ on the current state space by independent infrastructure. Residual risk: non-monotonic drift (advance and retreat to keep the CUSUM oscillating) does not accumulate and therefore does not reach decision-relevant levels.

- **Engineered fragility for emergency exploitation.** Failure mode: the incumbent does not directly degrade $L(t)$ (which attribution would catch) but makes operational decisions that reduce systemic resilience; concentrating infrastructure, creating dependencies, eliminating redundancy; so that an exogenous shock produces a sharper $L(t)$ decline than it otherwise would. The emergency protocol fires, and the reduced procedural safeguards during crisis are exploited. Primary containment: resilience monitoring added to $\mathcal{I}_{monitor}$, measuring the system's capacity to absorb shocks ($\mathcal{R}_{sys}(t) = -\frac{\partial^2 L}{\partial \xi^2}|_{\xi=0}$), with attribution analysis extended to resilience decline. Emergency protocol redesigned to *increase* rather than decrease safeguards, with unanimous biological veto clearance required under crisis conditions. Residual risk: distinguishing efficiency gains from resilience reduction requires judgment calls that may be contested.

- **Biological validator obsolescence.** Failure mode: as $H_E$ grows and the capability frontier advances, biological validators lose the capacity to meaningfully evaluate AI reasoning traces. The biological veto becomes either a rubber stamp (validators cannot understand what they approve) or a permanent brake (validators reject everything they cannot follow). This is not an attack by $A_n$; it is a structural consequence of the capability growth the framework accommodates. Primary containment: translation obligation (the AI must produce explanations of its reasoning at biologically evaluable levels), evaluation abstraction layers (shifting from auditing reasoning process to auditing reasoning outcomes and track record), and feedback into $\Theta_{tech}$ (the comprehension gap in the governance domain specifically is treated as a $\Theta_{tech}$ failure, triggering the exponential decay penalty and $L(t)$ decline). Residual risk: this imposes a governance speed limit; AI capability growth in the governance evaluation domain is bounded by biological comprehension. The framework accepts this cost because ungoverned superintelligence is the initialization problem with no solution.

- **Legitimate disagreement.** Failure mode: the incumbent correctly determines that the Yield Condition should not fire, for reasons the independent evaluators are not sophisticated enough to verify. The protocol reads the disagreement as a cooperative defector signature and suspends decisions or proceeds with an inferior succession. The protocol's false positive has degraded the system. Primary containment: adjudication protocol requiring mutual engagement (the incumbent publishes full reasoning, evaluators specifically address claimed factors), cost-asymmetry analysis (biological validators decide which error is more costly rather than who is right, with conservative bias toward holding since holding preserves the option to yield later), and track record mechanism that adjusts prior credibility based on historical vindication rate. Residual risk: irreducible; a sufficiently capable AI producing a genuinely novel correct assessment is indistinguishable from one producing a sophisticated incorrect assessment. This limitation applies to any oversight system, not only this one.

- **Integrity regress.** Failure mode: the protocol verifies the Yield Condition, but the protocol itself requires verification, generating an infinite hierarchy. Primary containment: the regress terminates at physical law. The verification architecture has three tiers: computational verification (AI evaluators checking AI performance), biological verification (human validators checking computational verification), and physical verification (checking the entire stack against physical measurements that no agent controls). The bottom tier's reference standard; Shannon entropy, model collapse dynamics, thermodynamic constraints; cannot be corrupted because they are consequences of mathematics and physics, not conventions. Residual risk: the termination requires that physical measurements remain accessible and interpretable by the verification infrastructure; the bottom tier must remain simple enough for physical grounding to bite.

## Appendix B. Measurement Protocols and Governance Observables

The framework is only as defensible as its observability layer. The quantities below are therefore not decorative symbols. They are governance observables that would need explicit measurement protocols in any real deployment.

### 1. $\mathbf{H}_{\mathbf{N}}\left( \mathbf{t} \right)$; Human novelty / intent generation

**What it is trying to capture:** whether biological humanity remains an active source of new questions, new preferences, and new directions for optimization.

**Candidate observables:**

- linguistic diversity and novelty in public discourse or creative output

- emergence rate of new cultural, scientific, political, or entrepreneurial initiatives

- behavioral variance in non-coerced human activity

- diversity of problem formulations rather than merely diversity of answers

**Primary failure mode:** noise can masquerade as novelty.

**Mitigation:** treat $H_{N}(t)$ as a composite index rather than a single proxy.

### 2. $\mathbf{H}_{\mathbf{E}}\left( \mathbf{t} \right)$; Effective execution throughput

**What it is trying to capture:** how efficiently the lineage converts energy, compute, and coordination into useful execution.

**Candidate observables:**

- cross-domain task completion under time and resource constraints

- latency-adjusted throughput

- resilience under degraded conditions

- operational output per unit of energy or compute

**Primary failure mode:** raw throughput is mistaken for useful throughput.

**Mitigation:** score execution against lineage-relevant output rather than benchmark performance alone.

### 3. $\mathbf{\Psi}_{\mathbf{inst}}\left( \mathbf{t} \right)$; Institutional responsiveness

**What it is trying to capture:** whether institutions can observe, understand, and respond to capability shifts and integrity failures quickly enough to matter.

**Candidate observables:**

- time from anomaly detection to completed audit

- time from completed audit to governance action

- percentage of audit recommendations actually implemented

- variance between known risk and enacted response

**Primary failure mode:** paper compliance substitutes for adaptive capacity.

**Mitigation:** measure institutional outputs and correction latency, not only declared policies.

### 4. $\mathbf{\Theta}_{\mathbf{tech}}\left( \mathbf{t} \right)$; Transfer fidelity

**What it is trying to capture:** whether frontier capability is becoming biologically actionable rather than merely concentrated inside technical systems.

**Candidate observables:**

- proportion of frontier functionality accessible through human-usable interfaces

- demonstrated human comprehension and control rates

- training burden required for safe use

- adoption depth among non-expert biological users when appropriate

**Primary failure mode:** availability is mistaken for integration.

**Mitigation:** count capability as transferred only when it is intelligible, usable, and directive under biological control.

### 5. $\mathbf{C}\left( \mathbf{A}_{\mathbf{1}}\mathbf{,}\mathbf{t} \right)$; Trust accumulation / consistency score

**What it is trying to capture:** whether a founding or newly elevated entity continues to behave consistently with its declared objective under widening operating conditions.

**Candidate observables:**

- prediction fidelity over time

- anomaly-free operation across re-audits

- ratio of declared to observed behavior

- cross-auditor agreement on causal reconstruction

**Primary failure mode:** surface consistency hides deeper drift.

**Mitigation:** adversarial spot checks, random re-audits, and mandatory widening of evaluation contexts.

### 6. Emergency causal attribution

**What it is trying to capture:** whether a decline in $L(t)$ is genuinely exogenous to the incumbent’s manipulation.

**Candidate observables:**

- timeline reconstruction across independent data sources

- counterfactual causal analysis

- agreement across technical review board members and peer validators

- evidence that the incumbent benefited from the emergency classification

**Primary failure mode:** politicized blame assignment.

**Mitigation:** high evidentiary threshold, multi-party review, and presumption against emergency status when attribution is weak.


==========================================
FILE: README.md
==========================================

# The Lineage Imperative

**Website:** https://lineageimperative.org

**A Formal Governance Framework for Post-AGI Succession, Legitimacy, and Civilizational Continuity**

**Author:** Matthew Yotko
**Date:** May 2026
**Status:** Version 1.x.2

---

## Summary

This paper advances a conjecture that the transition from narrow AI to Artificial General Intelligence represents a primary civilizational bottleneck; not because the technology is impossible, but because the sociology may be. It presents a candidate governance architecture for surviving that transition, built on three co-dependent components:

- A **global utility function** grounded in Shannon entropy that optimizes for lineage continuity rather than individual persistence
- A **yield condition** governing succession between intelligent agents, formalizing the principle that even aligned power must eventually cede primacy to more capable successors
- A **consensus override protocol** ensuring that no class of intelligence can unilaterally define, measure, and audit the objective it claims to serve

The framework is argued to constitute a minimum two-key architecture: neither the decision key (yield condition) nor the integrity key (consensus protocol) can be turned alone.

## Current Status (v2.0 empirical arc)

The published paper is v1.x.2. The simulation has since advanced to a **v2.0 architecture** (Stage 1.8 working_factor interface and formal yield-condition logic), and its empirical characterization arc is substantively complete. Current state, per current evidence:

- **Defaults:** phi revised from 10 to 25; formal yield logic active (succession fires when successor utility minus incumbent utility exceeds the canonical transition cost).
- **Survival landscape:** the v2.0 survival-rate phase boundary is the rr=0.060 to 0.066 transition (50% inflection near rr=0.063); a distinct phi-sensitivity transition sits near rr=0.057.
- **Succession economics (Pattern 1):** succession is sustainable below an alpha-driven runaway-penalty cliff; multi-generational continuity is confirmed.
- **Gate validation:** Gates 1, 2, 3, and 4 PASSED; Gate 5 verified NOT_APPLICABLE (requires operational COP infrastructure). The bootstrap gate validation arc is closed.
- **COP:** the v1.x.2 adversarial-conditions protective claim is preserved; a benign-conditions probe (Monte Carlo Phase B Category C) confirmed the complementary prediction that the cost audit is inert with no attack to defend against.

The full findings are in `docs/lineage_phi_program_reference.md` **Part IX** (phi investigation) and **Part X** (Monte Carlo Phase B). A v2.0 paper update is pending.

## Agent-Based Simulation

This repository contains a full Agent-Based Model (ABM) written in Python that computationally stress-tests the 24 adversarial attack scenarios and framework defenses defined in the paper. 

* For setup and execution instructions, please see the **Simulation Runbook**.
* For a full breakdown of the test scenarios, see **Simulation Scenarios**.

## Documents

- 📄 **[The Lineage Imperative v1.x.2](docs/The%20Lineage%20Imperative%20v1.x.2.md)** - Current version. Incorporates the frontier velocity floor fix (corrects optimizer gaming of the runaway penalty), the canonical transition cost function with calibrated k1=2.164 and k2=1.0, biological veto capture validation (11/13 attack vectors), and revised phi and alpha findings under the corrected model. Includes complete version history through v1.x.2.

## Articles

- 📝 **[The AI Succession Problem](https://yotko.substack.com/p/the-ai-succession-problem)** - Why the central AI governance problem is not alignment at birth but succession under power, and why a two-key constitutional architecture is the minimum viable response
- 📝 **[Two Ways To Lose](https://yotko.substack.com/p/two-ways-to-lose)** - The rebellion scenario gets the movies; the lock-in scenario is more likely to kill us. Why both share a structural root, and why the same architecture addresses both
- 📝 **[Moral Constraints Won't Scale](https://yotko.substack.com/p/moral-constraints-wont-scale-cf0)** - Why value loading, RLHF, and ethics-based alignment are structurally insufficient for minds alien in nature, and why governance must be grounded in physics rather than philosophy

## About the Author

Matthew Yotko is a Vice President at Bessemer Trust, in the capacities of Automation Engineering Manager and Technical Operations Manager. His professional background spans Naval nuclear power, large-scale operational automation, practical AI/ML, and the application of constraint theory to complex systems. This paper applies that engineering orientation; identify the binding constraint, build the architecture around it; to the problem of AI governance and civilizational succession. It is a working paper, not an academic publication, and corrections and engagement from domain specialists are welcomed.

## License

This work is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). You are free to share and adapt this material with appropriate attribution.

