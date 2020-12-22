import pytest
import asyncio
import dataclasses
import async_timeout
from royalnet.engineer import exc
from royalnet.engineer.wrench import screw, nuts


@dataclasses.dataclass()
class QueueSource:
    queue: asyncio.Queue
    source: screw.ScrewSource


@pytest.fixture
def qs() -> QueueSource:
    queue = asyncio.Queue()
    source = screw.ScrewSource(func=queue.get)
    return QueueSource(queue=queue, source=source)


def test_creation():
    async def one():
        return 1
    screw.ScrewSource(func=one)


class TestSingle:
    def test_success(self, qs: QueueSource):
        await qs.queue.put(1)
        assert await qs.source.single() == 1

    def test_timeout(self, qs: QueueSource):
        with pytest.raises(asyncio.TimeoutError):
            async with async_timeout.timeout(0.005):
                await qs.source.single()

    def test_error_propagation(self):
        class TestError(Exception):
            pass

        async def error():
            raise TestError()

        source = screw.ScrewSource(func=error)

        with pytest.raises(TestError):
            await source.single()

    def test_args_propagation(self):
        async def arg(*args):
            return args

        source = screw.ScrewSource(func=arg)
        assert await source.single(1) == 1


class TestNut:
    def test_pass(self, qs: QueueSource):
        await qs.queue.put(1)
        assert await (qs.source | nuts.Pass()) == 1

    def test_discard(self, qs: QueueSource):
        await qs.queue.put(1)