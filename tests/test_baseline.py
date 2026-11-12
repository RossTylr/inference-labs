import pytest

from inference_labs.baseline import LENS


@pytest.mark.parametrize("call", [lambda: LENS.diagnose({}), lambda: LENS.treat({}), LENS.scorecard])
def test_baseline_is_a_stub_until_o1_is_closed(call):
    with pytest.raises(NotImplementedError, match="O-1"):
        call()
