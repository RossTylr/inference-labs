from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def small_sample():
    from inference_labs.generator import sample

    return sample(20_000, 42, return_truth=True)
