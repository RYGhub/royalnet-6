import pytest
from royalnet.engineer import sentry, wrench

pytestmark = [pytest.mark.asyncio]


@pytest.fixture
def s() -> sentry.Sentry:
    return sentry.Sentry()


class TestSentry:
    def test_creation(self, s: sentry.Sentry):
        assert s
        assert isinstance(s, sentry.Sentry)

    async def test_put(self, s: sentry.Sentry):
        await s.queue.put(None)

    async def test_get(self, s: sentry.Sentry):
        await s.queue.put(None)
        assert await s.queue.get() is None

    async def test_source(self, s: sentry.Sentry):
        await s.queue.put(None)
        f = s.source()
        assert f
        assert isinstance(f, wrench.ScrewSource)
        assert hasattr(f, "pipe")
