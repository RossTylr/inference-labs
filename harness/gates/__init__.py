"""One module per gate (PRD section 3). Each exposes `check(root, slice_id, ...) -> GateResult`.

Every gate listed here has a planted-defect test in tests/planted/ with the same number (G-12).
"""
from harness.gates import (
    g01_manifest,
    g02_tests,
    g03_determinism,
    g04_calibration,
    g05_provenance,
    g06_labels,
    g07_notebook,
    g08_parity,
    g09_synthetic_app,
    g10_evidence,
    g11_sceptic,
    g12_planted,
    g13_frozen,
)

GATES = {
    "G-1": g01_manifest.check,
    "G-2": g02_tests.check,
    "G-3": g03_determinism.check,
    "G-4": g04_calibration.check,
    "G-5": g05_provenance.check,
    "G-6": g06_labels.check,
    "G-7": g07_notebook.check,
    "G-8": g08_parity.check,
    "G-9": g09_synthetic_app.check,
    "G-10": g10_evidence.check,
    "G-11": g11_sceptic.check,
    "G-12": g12_planted.check,
    "G-13": g13_frozen.check,
}
