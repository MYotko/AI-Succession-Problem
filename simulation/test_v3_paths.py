"""Scoped pytest artifact directories, independent of pytest's default temp root."""
from pathlib import Path
import tempfile
import pytest


@pytest.fixture
def tmp_path():
    root = Path(__file__).resolve().parent / 'v3' / '_pytest_v3'
    root.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix='case_', dir=root))
