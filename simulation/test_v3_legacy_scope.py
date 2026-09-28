"""Optional pytest plugin for legacy read-only external-cwd path probes.

Load with -p test_v3_legacy_scope and PYTHONPATH=simulation. Only the two
legacy AST path probes use an existing external directory as their cwd.
They write nothing there. Other tmp_path users get a unique scoped
directory without first constructing pytest's external default temp root.
"""

from pathlib import Path
import tempfile
import pytest


@pytest.fixture(name="tmp_path")
def scoped_legacy_tmp_path(request):
    if request.node.path.name == "test_output_paths.py" and request.node.originalname in (
        "test_module_paths_ignore_launch_directory", "test_smoke_output_root"
    ):
        return Path(__file__).resolve().parents[2]
    root = Path(__file__).resolve().parent / "v3" / "_pytest_v3"
    root.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix="legacy_", dir=root))
