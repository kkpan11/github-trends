from asyncio import sleep
from datetime import timedelta

from aiounittest.case import AsyncTestCase

from src.helper.alru_cache import alru_cache


class TestTemplate(AsyncTestCase):
    async def test_basic_alru_cache(self):
        count = 0

        @alru_cache()
        async def f(x: int) -> int:
            nonlocal count
            count += 1
            return (True, x)  # type: ignore

        assert count == 0
        assert await f(1) == 1
        assert count == 1
        assert await f(1) == 1
        assert count == 1
        assert await f(2) == 2
        assert count == 2
        assert await f(2) == 2
        assert count == 2
        assert await f(1) == 1
        assert count == 2

    async def test_alru_cache_with_flag(self):
        count = 0

        @alru_cache()
        async def f(x: int) -> int:
            nonlocal count
            count += 1
            return (count % 2 == 0, x)  # type: ignore

        assert count == 0
        assert await f(1) == 1
        assert count == 1
        assert await f(1) == 1
        assert count == 2
        assert await f(2) == 2
        assert count == 3
        assert await f(3) == 3
        assert count == 4
        assert await f(3) == 3
        assert count == 4

    async def test_alru_cache_with_maxsize(self):
        count = 0

        @alru_cache(max_size=2)
        async def f(x: int) -> int:
            nonlocal count
            count += 1
            return (True, x)  # type: ignore

        assert count == 0
        assert await f(1) == 1
        assert count == 1
        assert await f(2) == 2
        assert count == 2
        assert await f(3) == 3
        assert count == 3
        assert await f(1) == 1
        assert count == 4

    async def test_alru_cache_with_ttl(self):
        count = 0

        @alru_cache(ttl=timedelta(milliseconds=1))
        async def f(x: int) -> int:
            nonlocal count
            count += 1
            return (True, x)  # type: ignore

        assert count == 0
        assert await f(1) == 1
        assert count == 1
        assert await f(1) == 1
        assert count == 1
        await sleep(0.01)
        assert await f(1) == 1
        assert count == 2

    async def test_alru_cache_with_ignore_cache(self):
        count = 0

        @alru_cache()
        async def f(x: int, ignore_cache: bool = False) -> int:
            nonlocal count
            count += 1
            return (True, x)  # type: ignore

        assert count == 0
        assert await f(1) == 1
        assert count == 1
        assert await f(1) == 1
        assert count == 1
        assert await f(1, ignore_cache=True) == 1
        assert count == 2

    async def test_alru_cache_with_update_cache(self):
        count = 0

        @alru_cache()
        async def f(
            x: int, ignore_cache: bool = False, update_cache: bool = False
        ) -> int:
            nonlocal count
            count += 1
            return (True, x)  # type: ignore

        assert count == 0
        assert await f(1) == 1
        assert count == 1
        assert await f(1) == 1
        assert count == 1
        assert await f(2, ignore_cache=True) == 2
        assert count == 2
        assert await f(2) == 2
        assert count == 3
        assert await f(3, ignore_cache=True, update_cache=True) == 3
        assert count == 4
        assert await f(3) == 3
        assert count == 4
