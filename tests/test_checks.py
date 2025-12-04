from netwatch.config import default_targets
from netwatch.checks import run_check, CheckResult


def test_run_check_returns_checkresult():
    target = default_targets()[0]
    result = run_check(target)

    assert isinstance(result, CheckResult)
    assert result.target == target
