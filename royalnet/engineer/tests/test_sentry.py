import pytest
from royalnet.engineer import sentry, wrench


@pytest.fixture
def s() -> sentry.Sentry:
    return sentry.Sentry()


def test_creation(s: sentry.Sentry):
    assert s
    assert isinstance(s, sentry.Sentry)


@pytest.mark.asyncio
async def test_put(s: sentry.Sentry):
    await s.queue.put(None)


@pytest.mark.asyncio
async def test_get(s: sentry.Sentry):
    await s.queue.put(None)
    assert await s.queue.get() is None


@pytest.mark.asyncio
async def test_source(s: sentry.Sentry):
    await s.queue.put(None)
    f = s.source()
    assert f
    assert isinstance(f, wrench.ScrewSource)
    assert hasattr(f, "pipe")
