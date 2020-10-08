import pytest
from ..asynccampaign import AsyncCampaign
from ..asyncchallenge import AsyncChallenge
from ..exc import *


@pytest.mark.asyncio
async def test_creation():
    async def gen():
        yield None, "Created!"

    campaign, data = await AsyncCampaign.create(start=gen())
    assert data == "Created!"


@pytest.mark.asyncio
async def test_send_receive():
    async def gen():
        ping = yield None
        assert ping == "Ping!"
        yield None, "Pong!"

    campaign, = await AsyncCampaign.create(start=gen())
    pong, = await campaign.next("Ping!")
    assert pong == "Pong!"


class FalseChallenge(AsyncChallenge):
    async def filter(self, data) -> bool:
        return False


@pytest.mark.asyncio
async def test_failing_check():
    async def gen():
        yield FalseChallenge()

    campaign, = await AsyncCampaign.create(start=gen())
    with pytest.raises(ChallengeFailedError):
        await campaign.next(None)


@pytest.mark.asyncio
async def test_switching():
    async def gen_1():
        yield gen_2()

    async def gen_2():
        yield None, "Post-init!"
        yield None, "Second message!"
        yield None

    campaign, data = await AsyncCampaign.create(start=gen_1())
    assert data == "Post-init!"
    data, = await campaign.next()
    assert data == "Second message!"
