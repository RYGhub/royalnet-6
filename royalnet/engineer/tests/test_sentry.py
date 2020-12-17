import pytest
import asyncio
import async_timeout
from .. import sentry, exc


@pytest.fixture
def s() -> sentry.Sentry:
    return sentry.Sentry()


class TestSentry:
    def test_creation(self, s: sentry.Sentry):
        assert s
        assert isinstance(s, sentry.Sentry)

    @pytest.mark.asyncio
    async def test_put(self, s: sentry.Sentry):
        await s.queue.put(None)

    @pytest.mark.asyncio
    async def test_get(self, s: sentry.Sentry):
        await s.queue.put(None)
        assert await s.queue.get() is None

    @pytest.mark.asyncio
    async def test_f(self, s: sentry.Sentry):
        await s.queue.put(None)
        f = s.f()
        assert f
        assert isinstance(f, sentry.Filter)
        assert hasattr(f, "get")


@pytest.fixture
def discarding_filter() -> sentry.Filter:
    async def discard(_):
        raise exc.Discard(None, "This filter discards everything!")

    return sentry.Filter(discard)


class TestFilter:
    def test_creation(self):
        f = sentry.Filter(lambda _: _)
        assert f
        assert isinstance(f, sentry.Filter)

    class TestGetSingle:
        @pytest.mark.asyncio
        async def test_success(self, s: sentry.Sentry):
            await s.queue.put(None)
            assert await s.f().get_single() is None

        @pytest.mark.asyncio
        async def test_failure(self, discarding_filter: sentry.Filter):
            with pytest.raises(exc.Discard):
                await discarding_filter.get_single()

    class TestGet:
        @pytest.mark.asyncio
        async def test_success(self, s: sentry.Sentry):
            await s.queue.put(None)
            assert await s.f().get() is None

        @pytest.mark.asyncio
        async def test_timeout(self, s: sentry.Sentry):
            with pytest.raises(asyncio.TimeoutError):
                async with async_timeout.timeout(0.05):
                    await s.f().get()
