# src/utils/throttle.py
from collections import defaultdict
from collections import deque
from collections.abc import Callable
import time


class LoginThrottle:
    """Blocks a key after too many failures within a sliding window (in-memory)."""

    def __init__(
        self,
        max_failures: int = 5,
        window_seconds: float = 300,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._max_failures = max_failures
        self._window = window_seconds
        self._clock = clock
        self._failures: defaultdict[str, deque[float]] = defaultdict(deque)

    def is_blocked(self, key: str) -> bool:
        return len(self._recent(key)) >= self._max_failures

    def record_failure(self, key: str) -> None:
        self._recent(key).append(self._clock())

    def reset(self, key: str) -> None:
        self._failures.pop(key, None)

    def _recent(self, key: str) -> deque[float]:
        failures = self._failures[key]
        cutoff = self._clock() - self._window
        while failures and failures[0] <= cutoff:
            failures.popleft()
        return failures
