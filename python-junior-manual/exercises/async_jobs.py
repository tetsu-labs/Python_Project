"""Bounded concurrent jobs; executor work uses injected synchronous function."""
import asyncio
from collections.abc import Callable, Iterable
from typing import TypeVar

T = TypeVar('T')
R = TypeVar('R')


async def map_bounded(items: Iterable[T], worker: Callable[[T], R], *, limit: int = 4) -> list[R]:
    """Run blocking jobs in threads while preserving input order."""
    if limit < 1:
        raise ValueError('limit must be >= 1')
    semaphore = asyncio.Semaphore(limit)

    async def one(item: T) -> R:
        async with semaphore:
            return await asyncio.to_thread(worker, item)

    return await asyncio.gather(*(one(item) for item in items))
