import pytest
from ..asynccampaign import AsyncCampaign
from ..asyncchallenge import AsyncChallenge
from ..exc import *


@pytest.mark.asyncio
async def test_creation():
    async def gen():
        yield

    await AsyncCampaign.create(start=gen())


@pytest.mark.asyncio
async def test_send_receive():
    async def gen():
        ping = yield
        assert ping == "Ping!"
        yield None, "Pong!"

    campaign = await AsyncCampaign.create(start=gen())
    pong, = await campaign.next("Ping!")
    assert pong == "Pong!"


class FalseChallenge(AsyncChallenge):
    async def filter(self, data) -> bool:
        return False


@pytest.mark.asyncio
async def test_failing_check():
    async def gen():
        yield

    campaign = await AsyncCampaign.create(start=gen(), challenge=FalseChallenge())
    with pytest.raises(ChallengeFailedError):
        await campaign.next()


@pytest.mark.asyncio
async def test_switching():
    async def gen_1():
        yield
        yield gen_2()

    async def gen_2():
        yield
        yield None, "Second message!"
        yield None

    campaign = await AsyncCampaign.create(start=gen_1())
    data, = await campaign.next()
    assert data == "Second message!"
