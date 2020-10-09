import pytest
from ..campaign import Campaign
from ..challenge import Challenge, TrueChallenge
from ..exc import *


def test_creation():
    def gen():
        yield

    Campaign.create(start=gen())


def test_send_receive():
    def gen():
        ping = yield
        assert ping == "Ping!"
        yield None, "Pong!"

    campaign = Campaign.create(start=gen())
    pong, = campaign.next("Ping!")
    assert pong == "Pong!"


class FalseChallenge(Challenge):
    def filter(self, data) -> bool:
        return False


def test_failing_check():
    def gen():
        yield

    campaign = Campaign.create(start=gen(), challenge=FalseChallenge())
    with pytest.raises(ChallengeFailedError):
        campaign.next()


def test_switching():
    def gen_1():
        yield
        yield gen_2()

    def gen_2():
        yield
        yield None, "Second message!"
        yield None

    campaign = Campaign.create(start=gen_1())
    data, = campaign.next()
    assert data == "Second message!"
