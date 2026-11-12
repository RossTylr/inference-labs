import importlib.util

import pandas as pd


def _script(root):
    spec = importlib.util.spec_from_file_location("make_fixtures", root / "tests" / "fixtures" / "make_fixtures.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_committed_fixtures_are_the_script_output(root):
    script = _script(root)
    for name, make in script.FIXTURES.items():
        assert (root / "tests" / "fixtures" / name).read_text() == script.as_csv(make())


def test_fixtures_have_the_stated_columns_and_only_synthetic_ids(root):
    script = _script(root)
    for name, columns in (("crash2.csv", script.CRASH2_COLUMNS), ("crash3.csv", script.CRASH3_COLUMNS)):
        frame = pd.read_csv(root / "tests" / "fixtures" / name)
        assert list(frame.columns) == columns
        assert frame["entryid"].str.startswith("SYN-").all()
        assert len(frame) == script.ROWS
