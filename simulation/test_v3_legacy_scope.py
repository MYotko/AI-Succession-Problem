"""Optional pytest plugin for legacy read-only external-cwd path probes.

Load with -p test_v3_legacy_scope and PYTHONPATH=simulation. Only the two
legacy AST path probes use an existing external directory as their cwd.
They write nothing there. Other tmp_path users retain pytest's fixture,
with --basetemp inside simulation/v3 to respect Stage A's write scope.
"""

from pathlib import Path
import pytest


@pytest.fixture(name="tmp_path")
def scoped_legacy_tmp_path(request, tmp_path):
    if request.node.path.name == "test_output_paths.py" and request.node.originalname in (
        "test_module_paths_ignore_launch_directory", "test_smoke_output_root"
    ):
        return Path(__file__).resolve().parents[2]
    return tmp_path
