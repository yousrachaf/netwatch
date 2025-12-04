from netwatch.config import Target
from netwatch.checks import (
    run_check,
    ping_check,
    tcp_check,
    http_check,
    CheckResult,
)


def test_run_check_returns_checkresult_for_ping():
    target = Target(name="Localhost ping", host="127.0.0.1", type="ping")
    result = run_check(target)
    assert isinstance(result, CheckResult)
    assert result.target == target


def test_ping_check_does_not_crash():
    target = Target(name="Google DNS", host="8.8.8.8", type="ping")
    result = ping_check(target)
    assert isinstance(result, CheckResult)


def test_tcp_check_without_port_fails_cleanly():
    target = Target(name="Missing port", host="localhost", type="tcp")
    result = tcp_check(target)
    assert isinstance(result, CheckResult)
    assert result.success is False
    assert "port" in result.message.lower()


def test_http_check_does_not_crash():
    target = Target(name="GitHub API", host="api.github.com", type="http", path="/")
    result = http_check(target)
    assert isinstance(result, CheckResult)
