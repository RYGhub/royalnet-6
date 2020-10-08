import pytest
from ..campaign import Campaign


def test_creation():
    def gen():
        yield
    campaign = Campaign.create(start=gen())
    assert campaign


def test_sending():
    def gen():
        hello = yield
        assert hello == "Hello world!"
        yield
    campaign = Campaign.create(start=gen())
    campaign.next("Hello world!")


def test_receiving():
    def gen():
        yield
        yield "Hello world!"
    campaign = Campaign.create(start=gen())
    response = campaign.next()
    assert response == "Hello world!"


def test_switching():
    def gen_1():
        yield
        yield gen_2()

    def gen_2():
        yield "Post-init!"
        yield "Second message!"
        yield
    campaign = Campaign.create(start=gen_1())
    response = campaign.next()
    assert response == "Post-init!"
    response = campaign.next()
    assert response == "Second message!"
