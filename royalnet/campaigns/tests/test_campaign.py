import pytest
from ..campaign import Campaign
from ..challenge import Challenge
from ..exc import *


def test_creation():
    def gen():
        yield None, "Created!"

    campaign, data = Campaign.create(start=gen())
    assert data == "Created!"


def test_send_receive():
    def gen():
        ping = yield None
        assert ping == "Ping!"
        yield None, "Pong!"

    campaign, = Campaign.create(start=gen())
    pong, = campaign.next("Ping!")
    assert pong == "Pong!"


class FalseChallenge(Challenge):
    def filter(self, data) -> bool:
        return False


def test_failing_check():
    def gen():
        yield FalseChallenge()

    campaign, = Campaign.create(start=gen())
    with pytest.raises(ChallengeFailedError):
        campaign.next()


def test_switching():
    def gen_1():
        yield gen_2()

    def gen_2():
        yield None, "Post-init!"
        yield None, "Second message!"
        yield None

    campaign, data = Campaign.create(start=gen_1())
    assert data == "Post-init!"
    data, = campaign.next()
    assert data == "Second message!"
