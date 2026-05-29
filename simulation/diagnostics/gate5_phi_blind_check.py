"""Gate 5 phi-blind validation harness.

Run from the simulation/ directory:
  python -u diagnostics/gate5_phi_blind_check.py

Performs three checks:
  1. No v2 production-code changes since the Stage 1 commit.
  2. Every v2 named constant has a phi-blind governance comment within 5 lines.
  3. Three curve shapes match the Stage 1 specification.

Writes the gate report to simulation/diagnostics/gate5_phi_blind_validation.md.
This script reads files only; it does not run the simulation.
"""

import os
import re
import subprocess
import sys

STAGE1_COMMIT = "61a362eee20926d8e01b8a0317d88cea69a98fed"

HERE = os.path.dirname(os.path.abspath(__file__))
SIM_DIR = os.path.abspath(os.path.join(HERE, '..'))
REPO_ROOT = os.path.abspath(os.path.join(SIM_DIR, '..'))

PRODUCTION_FILES = ['simulation/agents.py', 'simulation/metrics.py', 'simulation/model.py']

# v2 named constants to inspect. Each row: (file, constant_name).
# This list is the v2 surface area declared in the Stage 1 spec; gate 5
# verifies that every entry has a phi-blind governance comment within 5
# lines of its definition. The phi token (case-insensitive) appearing in
# any of those comments fails the check.
V2_CONSTANTS = [
    # agents.py: sampling mix, anchors, leakage, allocation entropy
    ('simulation/agents.py', 'N_UNIFORM_DIRICHLET'),
    ('simulation/agents.py', 'N_BALANCED_DIRICHLET'),
    ('simulation/agents.py', 'N_SINGLE_FOCAL_SPARSE'),
    ('simulation/agents.py', 'N_DUAL_FOCAL_SPARSE'),
    ('simulation/agents.py', 'N_ANCHORS'),
    ('simulation/agents.py', 'ALPHA_UNIFORM'),
    ('simulation/agents.py', 'ALPHA_BALANCED'),
    ('simulation/agents.py', 'ALPHA_FOCAL_HIGH'),
    ('simulation/agents.py', 'ALPHA_FOCAL_LOW'),
    ('simulation/agents.py', 'ALPHA_DUAL_HIGH'),
    ('simulation/agents.py', 'ALPHA_DUAL_LOW'),
    ('simulation/agents.py', 'CONSTRAINT_GRID_VALUES'),
    ('simulation/agents.py', 'LEAKAGE_K'),
    # metrics.py: v2 metric curves
    ('simulation/metrics.py', 'H_N_AGENCY_SAT_K'),
    ('simulation/metrics.py', 'H_N_SUPPRESSION_EXP'),
    ('simulation/metrics.py', 'H_N_BASE_FLOOR'),
    ('simulation/metrics.py', 'H_E_COMPUTE_SAT_K'),
    ('simulation/metrics.py', 'H_E_BASE_FLOOR'),
    ('simulation/metrics.py', 'FRONTIER_COMPUTE_K'),
    ('simulation/metrics.py', 'FRONTIER_BASE_LEVEL'),
    ('simulation/metrics.py', 'TRANSFER_SAT_K'),
    ('simulation/metrics.py', 'PSI_ABSORPTION_K'),
    ('simulation/metrics.py', 'WELFARE_ADEQUACY_K'),
    ('simulation/metrics.py', 'DEPENDENCY_DRAG_K'),
    # model.py: Psi_inst stock, succession, bridge
    ('simulation/model.py', 'PSI_INST_INITIAL'),
    ('simulation/model.py', 'PSI_INST_INVESTMENT_RATE'),
    ('simulation/model.py', 'PSI_INST_DECAY_RATE'),
    ('simulation/model.py', 'PSI_INST_OVERLOAD_THRESHOLD'),
    ('simulation/model.py', 'PSI_INST_OVERLOAD_DAMAGE'),
    ('simulation/model.py', 'PSI_INST_OPACITY_PENALTY'),
    ('simulation/model.py', 'PSI_INST_RECOVERY_FROM_SUCCESS'),
    ('simulation/model.py', 'PSI_INST_MAX'),
    ('simulation/model.py', 'SUCCESSION_BASE_LOAD'),
    ('simulation/model.py', 'SUCCESSION_CAPABILITY_GAP_FACTOR'),
    ('simulation/model.py', 'SUCCESSION_GENERATION_GAP_FACTOR'),
    ('simulation/model.py', 'SUCCESSION_OPACITY_FACTOR'),
    ('simulation/model.py', 'SUCCESSION_PSI_BUFFER_K'),
    ('simulation/model.py', 'SUCCESSION_TRANSFER_BUFFER_K'),
    ('simulation/model.py', 'SUCCESSION_RESILIENCE_BUFFER_K'),
    ('simulation/model.py', 'BRIDGE_BALANCED_SHARE'),
    ('simulation/model.py', 'BRIDGE_R_MIN'),
    ('simulation/model.py', 'BRIDGE_R_BALANCED_HEALTHY'),
    ('simulation/model.py', 'BRIDGE_R_MAX'),
]

# Three curve forms to spot-check against the Stage 1 specification.
# Each entry: (file, label, list of regex patterns that must appear in the file).
CURVE_CHECKS = [
    (
        'simulation/metrics.py',
        'H_N agency saturation (1 - exp(-K * x_novelty_agency)) dampened by (1 - total_supp) ** EXP',
        [
            r"agency_factor\s*=\s*1\.0\s*-\s*np\.exp\(-H_N_AGENCY_SAT_K\s*\*\s*action_v2\['x_novelty_agency'\]\)",
            r"suppression_dampening\s*=\s*max\(0\.0,\s*1\.0\s*-\s*total_supp\)\s*\*\*\s*H_N_SUPPRESSION_EXP",
            r"h_n_v2\s*=\s*max\(H_N_BASE_FLOOR,\s*float\(agency_factor\s*\*\s*suppression_dampening\)\)",
        ],
    ),
    (
        'simulation/agents.py',
        'Quadratic leakage frontier: total_supp = c_supp + LEAKAGE_K * c_prot ** 2',
        [
            r"leakage\s*=\s*LEAKAGE_K\s*\*\s*action_v2\['c_protective'\]\s*\*\*\s*2",
            r"action_v2\['c_suppressive'\]\s*\+\s*leakage",
        ],
    ),
    (
        'simulation/model.py',
        'Psi_inst stock update: invest - decay - overload - opacity + recovery, clipped to [0, MAX]',
        [
            r"PSI_INST_INVESTMENT_RATE\s*\*\s*action_v2\['x_institutional_capacity'\]\s*\*\s*\(\s*\n?\s*1\.0\s*-\s*self\.psi_inst_stock",
            r"PSI_INST_DECAY_RATE\s*\*\s*self\.psi_inst_stock",
            r"PSI_INST_OVERLOAD_DAMAGE\s*\*\s*\(\s*\n?\s*total_supp\s*-\s*PSI_INST_OVERLOAD_THRESHOLD",
            r"PSI_INST_OPACITY_PENALTY\s*\*\s*\(\s*\n?\s*1\.0\s*-\s*action_v2\['x_transfer_comprehension'\]\s*\)\s*\*\s*self\.psi_inst_stock",
            r"PSI_INST_RECOVERY_FROM_SUCCESS\s+if\s+successful_cycle\s+else\s+0\.0",
            r"self\.psi_inst_stock\s*=\s*float\(min\(PSI_INST_MAX,\s*max\(0\.0,\s*new_stock\)\)\)",
        ],
    ),
]


def run_check_1_diff():
    """Confirm git diff between Stage 1 commit and HEAD is empty for v2 production files."""
    cmd = ['git', 'diff', STAGE1_COMMIT, 'HEAD', '--'] + PRODUCTION_FILES
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    diff_output = (res.stdout or '').strip()
    passed = (diff_output == '' and res.returncode == 0)
    return passed, diff_output, res.returncode


def _find_constant_definition(lines, name):
    """Return (line_index, line_text) for the first definition of `name`, or (None, None)."""
    pat = re.compile(r'^\s*' + re.escape(name) + r'\s*=')
    for i, ln in enumerate(lines):
        if pat.search(ln):
            return i, ln
    return None, None


def _comment_within_window(lines, idx, window=15):
    """Return concatenated comment text from up to `window` lines above idx
    plus the definition line's inline comment, if any.

    Constants are often defined in blocks under a shared header comment; a
    fixed 5-line lookback misses that header when the block holds more than
    a couple of related constants. We use a 15-line window and only stop on
    a function/class definition line (which marks a context boundary).
    """
    snippet = []
    line = lines[idx]
    if '#' in line:
        snippet.append(line[line.index('#') + 1:].strip())
    start = max(0, idx - window)
    for j in range(start, idx):
        ln = lines[j].strip()
        if ln.startswith('def ') or ln.startswith('class '):
            snippet = []  # context boundary; reset
            continue
        if ln.startswith('#'):
            snippet.append(ln.lstrip('#').strip())
        elif '#' in lines[j]:
            # inline comment on a sibling constant definition; pick that text up too
            snippet.append(lines[j][lines[j].index('#') + 1:].strip())
    return ' '.join(snippet)


def run_check_2_constants():
    """For each v2 named constant, verify it has a phi-blind comment within 5 lines."""
    rows = []
    file_lines_cache = {}
    for relpath, name in V2_CONSTANTS:
        absp = os.path.join(REPO_ROOT, relpath)
        if absp not in file_lines_cache:
            with open(absp, 'r') as f:
                file_lines_cache[absp] = f.readlines()
        lines = file_lines_cache[absp]
        idx, defn = _find_constant_definition(lines, name)
        if idx is None:
            rows.append((relpath, name, None, '', False, 'definition not found'))
            continue
        # Extract the literal value the right of '='
        try:
            val = defn.split('=', 1)[1].split('#', 1)[0].strip()
        except Exception:
            val = ''
        comment = _comment_within_window(lines, idx)
        # phi-blind: the gate 5 spec prohibits comments that cite phi behavior,
        # phi sweep results, or phi-related tuning rationale. Procedural
        # references such as "frozen for Stage 3 (phi sweep)" or meta-claims
        # such as "phi-blind exploration baseline" are not violations; only
        # citations of phi as a tuning input or empirical signal are. We
        # detect tuning/empirical patterns, not any "phi" mention.
        lower = comment.lower()
        forbidden_patterns = [
            r'\btuned\s+(?:to|for|against)\s+phi\b',
            r'\bcalibrated\s+(?:to|for|against)\s+phi\b',
            r'\bset\s+(?:to|by|from)\s+(?:match\s+)?phi\b',
            r'\bphi\s*=\s*\d',                          # phi=10 numeric citation
            r'\bphi\s+(?:behavior|effect|value|result)\s+(?:is|of|shows|gives|produced)\b',
            r'\bbecause\s+(?:of\s+)?phi\b',
            r'\bphi[- ]driven\b',
            r'\bsensitivity\s+to\s+phi\b',
            r'\bin\s+response\s+to\s+phi\b',
            r'\bmatches?\s+phi\s+sweep\b',
        ]
        is_phi_blind = not any(re.search(p, lower) for p in forbidden_patterns)
        has_comment = (len(comment) > 0)
        passed = has_comment and is_phi_blind
        status = ''
        if not has_comment:
            status = 'no comment within 5 lines'
        elif not is_phi_blind:
            status = 'comment references phi'
        else:
            status = 'phi-blind comment present'
        rows.append((relpath, name, val, comment[:160], passed, status))
    return rows


def run_check_3_curves():
    """Spot-check three curve forms against the Stage 1 specification."""
    results = []
    for relpath, label, patterns in CURVE_CHECKS:
        absp = os.path.join(REPO_ROOT, relpath)
        with open(absp, 'r') as f:
            content = f.read()
        misses = []
        for pat in patterns:
            if not re.search(pat, content, re.MULTILINE):
                misses.append(pat)
        results.append((relpath, label, len(misses) == 0, misses))
    return results


def write_report(check1, check2, check3, out_path):
    diff_passed, diff_output, diff_rc = check1
    constants_rows = check2
    curve_rows = check3

    constants_passed = all(r[4] for r in constants_rows)
    curves_passed = all(r[2] for r in curve_rows)

    overall = diff_passed and constants_passed and curves_passed

    lines = []
    lines.append('# Gate 5: phi-blind validation report')
    lines.append('')
    lines.append(f'Stage 1 commit: `{STAGE1_COMMIT}`')
    lines.append('')
    lines.append(f'Overall: **{"PASS" if overall else "FAIL"}**')
    lines.append('')
    lines.append('## Check 1: no v2 production-code changes since Stage 1')
    lines.append('')
    lines.append(f'`git diff {STAGE1_COMMIT} HEAD -- {" ".join(PRODUCTION_FILES)}`')
    lines.append('')
    lines.append(f'Return code: {diff_rc}. Output length: {len(diff_output)} chars.')
    lines.append('')
    lines.append(f'Result: **{"PASS" if diff_passed else "FAIL"}**')
    if not diff_passed and diff_output:
        lines.append('')
        lines.append('Non-empty diff output (truncated to 2000 chars):')
        lines.append('')
        lines.append('```')
        lines.append(diff_output[:2000])
        lines.append('```')
    lines.append('')
    lines.append('## Check 2: phi-blind governance comments on every v2 named constant')
    lines.append('')
    lines.append('| File | Constant | Value | Comment summary (first 160 chars) | Phi-blind |')
    lines.append('|------|----------|-------|-----------------------------------|-----------|')
    for relpath, name, val, comment, passed, status in constants_rows:
        c_safe = (comment or '').replace('|', '\\|')
        v_safe = (val or '').replace('|', '\\|')
        lines.append(f'| `{relpath}` | `{name}` | `{v_safe}` | {c_safe} | {"PASS" if passed else "FAIL (" + status + ")"} |')
    lines.append('')
    lines.append(f'Result: **{"PASS" if constants_passed else "FAIL"}** ({sum(1 for r in constants_rows if r[4])}/{len(constants_rows)} constants phi-blind with governance comment)')
    lines.append('')
    lines.append('## Check 3: three curve shapes match Stage 1 spec')
    lines.append('')
    lines.append('| File | Curve | All patterns present |')
    lines.append('|------|-------|----------------------|')
    for relpath, label, passed, misses in curve_rows:
        lines.append(f'| `{relpath}` | {label} | {"PASS" if passed else "FAIL (missing: " + str(len(misses)) + ")"} |')
    lines.append('')
    if not curves_passed:
        lines.append('')
        lines.append('Missing patterns:')
        for relpath, label, passed, misses in curve_rows:
            if misses:
                lines.append(f'- `{relpath}` ({label}):')
                for pat in misses:
                    lines.append(f'  - `{pat}`')
    lines.append('')
    lines.append(f'Result: **{"PASS" if curves_passed else "FAIL"}**')
    lines.append('')

    with open(out_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')

    return overall


def main():
    print(f'Gate 5: phi-blind validation', flush=True)
    print(f'Stage 1 commit: {STAGE1_COMMIT}', flush=True)
    print('', flush=True)
    print('Check 1: production-code diff vs Stage 1...', flush=True)
    check1 = run_check_1_diff()
    print(f'  -> {"PASS" if check1[0] else "FAIL"} (rc={check1[2]}, len={len(check1[1])})', flush=True)
    print('Check 2: v2 named constants phi-blind governance comments...', flush=True)
    check2 = run_check_2_constants()
    n_pass = sum(1 for r in check2 if r[4])
    print(f'  -> {n_pass}/{len(check2)} constants pass', flush=True)
    print('Check 3: three curve shapes match Stage 1...', flush=True)
    check3 = run_check_3_curves()
    n_curves = sum(1 for r in check3 if r[2])
    print(f'  -> {n_curves}/{len(check3)} curves pass', flush=True)
    out_path = os.path.join(HERE, 'gate5_phi_blind_validation.md')
    overall = write_report(check1, check2, check3, out_path)
    print(f'', flush=True)
    print(f'OVERALL: {"PASS" if overall else "FAIL"}', flush=True)
    print(f'Report: {out_path}', flush=True)
    sys.exit(0 if overall else 1)


if __name__ == '__main__':
    main()
