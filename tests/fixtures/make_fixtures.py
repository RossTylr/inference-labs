"""Synthetic stand-ins for the CRASH-2 and CRASH-3 data files (R-0.11).

    python tests/fixtures/make_fixtures.py

No real records. Every value is drawn from a seeded random generator, so the tests and continuous integration
run without the real files, which are read from a local path outside the repository and never committed (D-7).
Every identifier begins SYN- so a fixture row cannot be mistaken for a trial record.

The column names follow the trial data files as far as they are known, from general knowledge; they have not
been checked against the files, which need registration with freeBIRD. Confirm them when O-2 is closed. The
rates and ranges below are arbitrary assumptions with no clinical meaning.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROWS = 200

CRASH2_COLUMNS = [
    "entryid", "sex", "age", "injurytime", "injurytype", "sbp", "rr", "cc", "hr",
    "gcseye", "gcsmotor", "gcsverbal", "gcs", "treatment", "condition", "cause", "ddeath",
]
CRASH3_COLUMNS = [
    "entryid", "sex", "age", "injurytime", "sbp", "gcseye", "gcsmotor", "gcsverbal", "gcs",
    "pupilreact", "treatment", "death28", "headinjurydeath",
]


def _common(rng: np.random.Generator, prefix: str) -> dict:
    eye, motor, verbal = rng.integers(1, 5, ROWS), rng.integers(1, 7, ROWS), rng.integers(1, 6, ROWS)
    return {
        "entryid": [f"SYN-{prefix}-{i:04d}" for i in range(1, ROWS + 1)],
        "sex": np.where(rng.random(ROWS) < 0.8, "M", "F"),
        "age": rng.integers(18, 71, ROWS),
        "injurytime": np.round(rng.uniform(0.5, 8.0, ROWS), 1),
        "sbp": np.clip(np.rint(rng.normal(110, 25, ROWS)), 40, 200).astype(int),
        "gcseye": eye,
        "gcsmotor": motor,
        "gcsverbal": verbal,
        "gcs": eye + motor + verbal,
        "treatment": np.where(rng.random(ROWS) < 0.5, "TXA", "placebo"),
    }


def crash2() -> pd.DataFrame:
    rng = np.random.default_rng(2)
    cols = _common(rng, "C2")
    died = rng.random(ROWS) < 0.15
    cols.update({
        "injurytype": rng.choice(["blunt", "penetrating", "blunt and penetrating"], ROWS),
        "rr": rng.integers(10, 41, ROWS),
        "cc": rng.integers(1, 7, ROWS),
        "hr": rng.integers(50, 161, ROWS),
        "condition": np.where(died, "dead", "alive"),
        "cause": np.where(died, rng.choice(["bleeding", "head injury", "other"], ROWS), ""),
        "ddeath": np.where(died, rng.integers(0, 29, ROWS).astype(str), ""),
    })
    return pd.DataFrame(cols)[CRASH2_COLUMNS]


def crash3() -> pd.DataFrame:
    rng = np.random.default_rng(3)
    cols = _common(rng, "C3")
    died = rng.random(ROWS) < 0.2
    cols.update({
        "pupilreact": rng.choice(["both", "one", "none", "unable to assess"], ROWS),
        "death28": died.astype(int),
        "headinjurydeath": (died & (rng.random(ROWS) < 0.8)).astype(int),
    })
    return pd.DataFrame(cols)[CRASH3_COLUMNS]


def as_csv(frame: pd.DataFrame) -> str:
    return frame.to_csv(index=False, lineterminator="\n")


FIXTURES = {"crash2.csv": crash2, "crash3.csv": crash3}


def main() -> None:
    for name, make in FIXTURES.items():
        (HERE / name).write_text(as_csv(make()), encoding="utf-8")
        print(f"wrote tests/fixtures/{name}")


if __name__ == "__main__":
    main()
