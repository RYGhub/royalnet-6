import asyncio
import pytest


async def sleep_and_raise():
    await asyncio.sleep(0.001)
    raise Exception("Please except this gift!")


@pytest.mark.asyncio
class TestAsyncio:
    async def test_exception(self):
        with pytest.raises(Exception):
            await sleep_and_raise()
