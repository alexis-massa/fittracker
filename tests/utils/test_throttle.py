from src.utils.throttle import LoginThrottle


class _Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def test_not_blocked_before_reaching_the_failure_limit() -> None:
    throttle = LoginThrottle(max_failures=3)
    for _ in range(2):
        throttle.record_failure("alice")
    assert throttle.is_blocked("alice") is False


def test_blocked_once_the_failure_limit_is_reached() -> None:
    throttle = LoginThrottle(max_failures=3)
    for _ in range(3):
        throttle.record_failure("alice")
    assert throttle.is_blocked("alice") is True


def test_failures_are_tracked_per_key() -> None:
    throttle = LoginThrottle(max_failures=1)
    throttle.record_failure("alice")
    assert throttle.is_blocked("bob") is False


def test_block_expires_after_the_window() -> None:
    clock = _Clock()
    throttle = LoginThrottle(max_failures=1, window_seconds=60, clock=clock)
    throttle.record_failure("alice")
    clock.now += 61
    assert throttle.is_blocked("alice") is False


def test_reset_clears_recorded_failures() -> None:
    throttle = LoginThrottle(max_failures=1)
    throttle.record_failure("alice")
    throttle.reset("alice")
    assert throttle.is_blocked("alice") is False
