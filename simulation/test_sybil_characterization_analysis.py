import hashlib
import json
from pathlib import Path


HERE = Path(__file__).parent
REPO_ROOT = HERE.parent
RUN_DIR = (
    REPO_ROOT
    / 'data'
    / 'sybil_defense_scaling'
    / 'full_5ac6a2e_sybil_scaling_characterization_v1'
)
MANIFEST = RUN_DIR / 'full_5ac6a2e_manifest.json'
ANALYSIS = HERE / 'diagnostics' / 'sybil_defense_scaling_characterization_analysis.json'
REPORT = HERE / 'diagnostics' / 'sybil_defense_scaling_characterization_report.md'


def test_authoritative_manifest_hashes_and_counts():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    assert manifest['total_cells'] == 5175
    assert manifest['total_runs'] == 1_035_000
    assert manifest['n_per_cell'] == 200
    assert manifest['completed_counts'] == manifest['planned_counts']
    assert len(manifest['authoritative_artifacts']) == 3
    for artifact in manifest['authoritative_artifacts']:
        path = REPO_ROOT / artifact['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == artifact['sha256']


def test_analysis_uses_registered_fixed_cell_quantities():
    analysis = json.loads(ANALYSIS.read_text(encoding='utf-8'))
    assert analysis['crossover_computed'] is False
    assert analysis['ratio_collapse']['registered_verdict'] == 'noncollapse'
    assert len(analysis['ratio_collapse']['comparisons']) == 75
    assert len(
        analysis['primary_headline']['arm_records']['false_cluster_injection']
    ) == 600
    assert len(
        analysis['primary_headline']['arm_records']['measurement_corruption']
    ) == 600
    assert len(
        analysis['primary_headline']['arm_records'][
            'measurement_corruption_rank_visible'
        ]
    ) == 600
    assert len(
        analysis['ratio_sensitivity']['records']['false_cluster_injection']
    ) == 100
    assert len(analysis['complete_linkage']['records']) == 100


def test_report_orders_criterion_before_result_before_verdict():
    report = REPORT.read_text(encoding='utf-8')
    assert 'No crossover rank was computed or used.' in report
    for heading in (
        '## 1. Ratio-collapse slice',
        '## 2. Primary fixed-cell reading, per arm',
        '## 3. Headline floor question',
        '## 4. Ratio sensitivity',
        '## 5. Complete-linkage sensitivity',
    ):
        start = report.index(heading)
        next_heading = report.find('\n## ', start + len(heading))
        section = report[start:next_heading if next_heading != -1 else None]
        assert section.index('Criterion, quoted verbatim') < section.index('Result:')
        assert section.index('Result:') < section.index('Verdict:')
