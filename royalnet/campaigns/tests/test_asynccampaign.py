import pytest
import asyncio
from ..asynccampaign import AsyncCampaign


@pytest.mark.asyncio
async def test_creation():
    async def gen():
        yield
    campaign = await AsyncCampaign.create(start=gen())
    assert campaign


@pytest.mark.asyncio
async def test_sending():
    async def gen():
        hello = yield
        assert hello == "Hello world!"
        yield
    campaign = await AsyncCampaign.create(start=gen())
    await campaign.next("Hello world!")


@pytest.mark.asyncio
async def test_receiving():
    async def gen():
        yield
        yield "Hello world!"
    campaign = await AsyncCampaign.create(start=gen())
    response = await campaign.next()
    assert response == "Hello world!"


@pytest.mark.asyncio
async def test_switching():
    async def gen_1():
        yield
        yield gen_2()

    async def gen_2():
        yield "Post-init!"
        yield "Second message!"
        yield
    campaign = await AsyncCampaign.create(start=gen_1())
    response = await campaign.next()
    assert response == "Post-init!"
    response = await campaign.next()
    assert response == "Second message!"
