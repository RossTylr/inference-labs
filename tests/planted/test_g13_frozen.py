"""Planted defect for G-13: the generator edited after freezing, with no manifest version bump."""
from pathlib import Path

import yaml

from harness.gates import g13_frozen


def _repo(tmp_path: Path, version: int = 1) -> Path:
    gen = tmp_path / "src" / "inference_labs" / "generator.py"
    gen.parent.mkdir(parents=True)
    gen.write_text("SEED = 42\n")
    (tmp_path / "params.yaml").write_text("version: 1\n")
    frozen = {
        "version": 1,
        "generator_sha256": g13_frozen.file_sha256(gen),
        "params_sha256": g13_frozen.file_sha256(tmp_path / "params.yaml"),
    }
    (tmp_path / "manifest.yaml").write_text(yaml.safe_dump({"version": version, "frozen": frozen}))
    return tmp_path


def _bump(root: Path) -> None:
    manifest = yaml.safe_load((root / "manifest.yaml").read_text())
    manifest["version"] = 2
    (root / "manifest.yaml").write_text(yaml.safe_dump(manifest))


def test_unchanged_generator_passes(tmp_path):
    assert g13_frozen.check(_repo(tmp_path), 1).passed


def test_edited_generator_fails(tmp_path):
    root = _repo(tmp_path)
    (root / "src" / "inference_labs" / "generator.py").write_text("SEED = 43\n")
    result = g13_frozen.check(root, 1)
    assert not result.passed and "version bump" in result.reason


def test_edited_generator_with_bump_passes(tmp_path):
    root = _repo(tmp_path)
    (root / "src" / "inference_labs" / "generator.py").write_text("SEED = 43\n")
    _bump(root)
    assert g13_frozen.check(root, 1).passed


def test_not_yet_frozen_passes(tmp_path):
    (tmp_path / "manifest.yaml").write_text(yaml.safe_dump({"version": 1, "frozen": None}))
    assert g13_frozen.check(tmp_path, 0).passed
