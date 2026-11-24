import asyncio
import threading
import time
import pytest
from exercises.async_jobs import map_bounded


def test_order():
    assert asyncio.run(map_bounded([3, 1, 2], lambda n: n * 10, limit=2)) == [30, 10, 20]


def test_empty():
    assert asyncio.run(map_bounded([], lambda n: n)) == []


def test_invalid_limit():
    with pytest.raises(ValueError):
        asyncio.run(map_bounded([1], lambda n: n, limit=0))


def test_bounded_concurrency():
    active = 0
    peak = 0
    lock = threading.Lock()

    def worker(n):
        nonlocal active, peak
        with lock:
            active += 1
            peak = max(peak, active)
        time.sleep(0.015)
        with lock:
            active -= 1
        return n

    assert asyncio.run(map_bounded(range(12), worker, limit=3)) == list(range(12))
    assert 1 <= peak <= 3


def test_exception_propagates():
    def fail(n):
        if n == 2:
            raise RuntimeError('failed')
        return n
    with pytest.raises(RuntimeError, match='failed'):
        asyncio.run(map_bounded([1, 2], fail))
