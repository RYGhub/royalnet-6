import pytest
import asyncio
import async_timeout
import re
from royalnet.engineer import sentry, exc, blueprints


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


class ErrorTest(Exception):
    pass


def error_test(*_, **__):
    raise ErrorTest("This was raised by error_raiser.")


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
                async with async_timeout.timeout(0.001):
                    await s.f().get()

    @pytest.mark.asyncio
    async def test_filter(self, s: sentry.Sentry):
        await s.queue.put(None)
        await s.queue.put(None)
        await s.queue.put(None)

        assert await s.f().filter(lambda x: x is None, "Is not None").get_single() is None

        with pytest.raises(exc.Discard):
            await s.f().filter(lambda x: isinstance(x, type), error="Is not type").get_single()

        with pytest.raises(ErrorTest):
            await s.f().filter(error_test, error="Is error").get_single()

    @pytest.mark.asyncio
    async def test_map(self, s: sentry.Sentry):
        await s.queue.put(None)
        await s.queue.put(None)

        assert await s.f().map(lambda x: 1).get_single() == 1

        with pytest.raises(ErrorTest):
            await s.f().map(error_test).get_single()

    @pytest.mark.asyncio
    async def test_type(self, s: sentry.Sentry):
        await s.queue.put(1)
        await s.queue.put("no")

        assert await s.f().type(int).get_single() == 1

        with pytest.raises(exc.Discard):
            await s.f().type(int).get_single()

    @pytest.mark.asyncio
    async def test_msg(self, s: sentry.Sentry):
        class ExampleMessage(blueprints.Message):
            def __hash__(self):
                return 1

        msg = ExampleMessage()
        await s.queue.put(msg)
        await s.queue.put("no")

        assert await s.f().msg().get_single() is msg

        with pytest.raises(exc.Discard):
            await s.f().msg().get_single()

    class AvailableMessage(blueprints.Message):
        def __hash__(self):
            return 1

        def text(self) -> str:
            return "1"

    class NotAvailableMessage(blueprints.Message):
        def __hash__(self):
            return 2

        def text(self) -> str:
            raise exc.NotAvailableError()

    class NeverAvailableMessage(blueprints.Message):
        def __hash__(self):
            return 3

    @pytest.mark.asyncio
    async def test_requires(self, s: sentry.Sentry):
        avmsg = self.AvailableMessage()
        await s.queue.put(avmsg)
        assert await s.f().requires("text").get_single() is avmsg

        await s.queue.put(self.NotAvailableMessage())
        with pytest.raises(exc.Discard):
            await s.f().requires("text").get_single()

        await s.queue.put(self.NeverAvailableMessage())
        with pytest.raises(exc.NeverAvailableError):
            await s.f().requires("text").get_single()

        await s.queue.put(self.NotAvailableMessage())
        with pytest.raises(exc.NotAvailableError):
            await s.f().requires("text", propagate_not_available=True).get_single()

        await s.queue.put(self.NeverAvailableMessage())
        with pytest.raises(exc.Discard):
            await s.f().requires("text", propagate_never_available=False).get_single()

    @pytest.mark.asyncio
    async def test_field(self, s: sentry.Sentry):
        avmsg = self.AvailableMessage()
        await s.queue.put(avmsg)
        assert await s.f().field("text").get_single() == "1"

        await s.queue.put(self.NotAvailableMessage())
        with pytest.raises(exc.Discard):
            await s.f().field("text").get_single()

        await s.queue.put(self.NeverAvailableMessage())
        with pytest.raises(exc.NeverAvailableError):
            await s.f().field("text").get_single()

        await s.queue.put(self.NotAvailableMessage())
        with pytest.raises(exc.NotAvailableError):
            await s.f().field("text", propagate_not_available=True).get_single()

        await s.queue.put(self.NeverAvailableMessage())
        with pytest.raises(exc.Discard):
            await s.f().field("text", propagate_never_available=False).get_single()

    @pytest.mark.asyncio
    async def test_startswith(self, s: sentry.Sentry):
        await s.queue.put("yarrharr")
        await s.queue.put("yohoho")

        assert await s.f().startswith("yarr").get_single() == "yarrharr"

        with pytest.raises(exc.Discard):
            await s.f().startswith("yarr").get_single()

    @pytest.mark.asyncio
    async def test_endswith(self, s: sentry.Sentry):
        await s.queue.put("yarrharr")
        await s.queue.put("yohoho")

        assert await s.f().endswith("harr").get_single() == "yarrharr"

        with pytest.raises(exc.Discard):
            await s.f().endswith("harr").get_single()

    @pytest.mark.asyncio
    async def test_regex(self, s: sentry.Sentry):
        await s.queue.put("yarrharr")
        await s.queue.put("yohoho")

        assert isinstance(await s.f().regex(re.compile(r"[yh]arr")).get_single(), re.Match)

        with pytest.raises(exc.Discard):
            await s.f().regex(re.compile(r"[yh]arr")).get_single()

    @pytest.mark.asyncio
    async def test_choices(self, s: sentry.Sentry):
        await s.queue.put("yarrharr")
        await s.queue.put("yohoho")

        assert await s.f().choices("yarrharr", "banana").get_single() == "yarrharr"

        with pytest.raises(exc.Discard):
            await s.f().choices("yarrharr", "banana").get_single()
