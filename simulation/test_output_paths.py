"""Hermetic output-path and snapshot-provenance regression tests."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SMOKES = ("run_sybil_defense_scaling_smoke.py", "run_sybil_two_dial_smoke.py")

# Evaluate only path definitions and main's output_root assignment, never a smoke
# or plotting import. This also avoids dependency installation and cache writes.
PATH_PROBE = r"""
import ast, json, os, sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Mapping
source = Path(sys.argv[1])
tree = ast.parse(source.read_text(encoding="utf-8"))
ns = {"__file__": str(source), "os": os, "Path": Path,
      "Any": Any, "Mapping": Mapping}
names = {"HERE", "REPO_ROOT", "DEFAULT_CONFIG", "DATA_DIR", "CHARTS_DIR"}
for node in tree.body:
    if (isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id in names for t in node.targets)):
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), "exec"), ns)
    if isinstance(node, ast.FunctionDef) and node.name == "resolve_output_root":
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), "exec"), ns)
if "DEFAULT_CONFIG" in ns:
    ns["config"] = json.loads(ns["DEFAULT_CONFIG"].read_text(encoding="utf-8"))
    override = None if sys.argv[2] == "default" else Path(sys.argv[2])
    ns["args"] = SimpleNamespace(output_root=override)
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    node = next(n for n in main.body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "output_root" for t in n.targets))
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), "exec"), ns)
    paths = {"output_root": ns["output_root"]}
else:
    paths = {key: ns[key] for key in ("DATA_DIR", "CHARTS_DIR") if key in ns}
print(json.dumps({key: {"raw": str(value), "absolute": str(Path(value).resolve()),
                       "is_absolute": Path(value).is_absolute()}
                  for key, value in paths.items()}))
"""


def _paths(filename, cwd, override="default"):
    result = subprocess.run(
        [sys.executable, "-B", "-c", PATH_PROBE,
         str(REPO_ROOT / "simulation" / filename), str(override)],
        cwd=cwd, capture_output=True, text=True, check=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    return json.loads(result.stdout)


@pytest.mark.parametrize("filename", ("monte_carlo.py", "visualization.py"))
def test_module_paths_ignore_launch_directory(filename, tmp_path):
    assert not tmp_path.is_relative_to(REPO_ROOT)
    outside = _paths(filename, tmp_path)
    assert outside == _paths(filename, REPO_ROOT)
    expected = {"DATA_DIR": REPO_ROOT / "data"}
    if filename == "monte_carlo.py":
        expected["CHARTS_DIR"] = REPO_ROOT / "docs" / "charts"
    assert set(outside) == set(expected)
    for name, value in outside.items():
        assert value["is_absolute"]
        assert Path(value["absolute"]) == expected[name]


@pytest.mark.parametrize("filename", SMOKES)
@pytest.mark.parametrize("case", ("default", "relative", "absolute"))
def test_smoke_output_root(filename, case, tmp_path):
    assert not tmp_path.is_relative_to(REPO_ROOT)
    config = json.loads(
        (REPO_ROOT / "simulation/config/sybil_defense_scaling.json").read_text(encoding="utf-8")
    )
    override = {"default": "default", "relative": "custom/results",
                "absolute": tmp_path / "preserved" / ".." / "results"}[case]
    outside = _paths(filename, tmp_path, override)
    assert outside == _paths(filename, REPO_ROOT, override)
    value = outside["output_root"]
    assert value["is_absolute"]
    expected = (REPO_ROOT / config["outputs"]["root"] if case == "default"
                else REPO_ROOT / override if case == "relative" else override)
    assert Path(value["absolute"]) == expected.resolve()
    if case == "absolute":
        assert value["raw"] == str(override)


@pytest.fixture
def snapshot(monkeypatch):
    path = REPO_ROOT / "scripts/generate_project_knowledge_snapshots.py"
    spec = importlib.util.spec_from_file_location("snapshot_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    calls = []
    for category in ("docs", "essays"):
        def collect(dry_run=False, category=category):
            calls.append((category, dry_run))
            return [(category + "/fixture.md", "Synthetic fixture\n")]
        monkeypatch.setitem(module.COLLECTORS, category, collect)
    return module, calls


@pytest.mark.parametrize("which", ("commit", "branch"))
@pytest.mark.parametrize("failure", ("command_error", "", "unknown"))
@pytest.mark.parametrize("allow", (False, True))
def test_snapshot_provenance_failure(snapshot, monkeypatch, tmp_path, capsys,
                                     which, failure, allow):
    module, calls = snapshot

    def git_output(command, **kwargs):
        field = "commit" if "--short" in command else "branch"
        if field == which:
            if failure == "command_error":
                raise subprocess.CalledProcessError(128, command)
            return failure.encode()
        return b"abcdef0" if field == "commit" else b"main"

    monkeypatch.setattr(module.subprocess, "check_output", git_output)
    output = tmp_path / "output"
    argv = ["snapshot", "--output-dir", str(output), "--categories", "docs"]
    if allow:
        argv.append("--allow-unknown-provenance")
    monkeypatch.setattr(sys, "argv", argv)
    if allow:
        module.main()
        assert calls == [("docs", False)]
        text = (output / "docs_snapshot.md").read_text(encoding="utf-8")
        inventory = (output / "INVENTORY.md").read_text(encoding="utf-8")
        assert "Commit: unknown" in text and "Branch: unknown" in text
        assert "Git commit at regeneration: unknown" in inventory
        assert "Branch: unknown" in inventory
    else:
        with pytest.raises(SystemExit) as error:
            module.main()
        assert error.value.code != 0
        assert not output.exists()
        assert not calls
        assert not list(tmp_path.iterdir())
    captured = capsys.readouterr()
    assert ("WARNING:" if allow else "ERROR:") in captured.err
    assert "git introspection failed" in captured.err
    assert ("--short" if which == "commit" else "--abbrev-ref") in captured.err
    if allow:
        assert "commit and branch as 'unknown'" in captured.err
    else:
        assert "Done." not in captured.out


@pytest.mark.parametrize("dry_run", (False, True))
def test_snapshot_known_provenance_and_categories(snapshot, monkeypatch, tmp_path,
                                                 capsys, dry_run):
    module, calls = snapshot
    monkeypatch.setattr(
        module.subprocess, "check_output",
        lambda command, **kwargs: b"abcdef0" if "--short" in command else b"main",
    )
    output = tmp_path / "output"
    argv = ["snapshot", "--output-dir", str(output), "--categories", "essays"]
    if dry_run:
        argv.append("--dry-run")
    monkeypatch.setattr(sys, "argv", argv)
    module.main()
    assert calls == [("essays", dry_run)]
    captured = capsys.readouterr()
    assert not captured.err
    assert "Commit: abcdef0, Branch: main" in captured.out
    if dry_run:
        assert "Dry run complete." in captured.out
        assert not output.exists()
    else:
        assert {p.name for p in output.iterdir()} == {"essays_snapshot.md", "INVENTORY.md"}
        text = (output / "essays_snapshot.md").read_text(encoding="utf-8")
        assert "Commit: abcdef0" in text and "Branch: main" in text
