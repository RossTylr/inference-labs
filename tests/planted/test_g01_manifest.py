"""Planted defects for G-1: a listed file removed, and an unlisted file added under src/."""
from pathlib import Path

import yaml

from harness.gates import g01_manifest


def _repo(tmp_path: Path) -> Path:
    (tmp_path / "src" / "pkg").mkdir(parents=True)
    (tmp_path / "src" / "pkg" / "a.py").write_text("x = 1\n")
    manifest = {"version": 1, "slices": {0: {"files": ["src/pkg/a.py"], "gates": ["G-1"], "blocked_by": []}}}
    (tmp_path / "manifest.yaml").write_text(yaml.safe_dump(manifest))
    return tmp_path


def test_clean_repo_passes(tmp_path):
    assert g01_manifest.check(_repo(tmp_path), 0).passed


def test_missing_listed_file_fails(tmp_path):
    root = _repo(tmp_path)
    (root / "src" / "pkg" / "a.py").unlink()
    result = g01_manifest.check(root, 0)
    assert not result.passed and "missing" in result.reason


def test_unlisted_file_fails(tmp_path):
    root = _repo(tmp_path)
    (root / "src" / "pkg" / "stray.py").write_text("y = 2\n")
    result = g01_manifest.check(root, 0)
    assert not result.passed and "stray.py" in result.reason
