import pytest
from royalnet.lazy import Lazy


def test_single_eval_no_args():
    lazy = Lazy(lambda: 1)
    assert not lazy.evaluated
    assert lazy._result is None
    result = lazy.evaluate()
    assert result == 1
    assert lazy.evaluated
    assert lazy._result == 1


def test_single_eval_with_args():
    lazy = Lazy(lambda a, b: a + b, 10, 10)
    result = lazy.evaluate()
    assert result == 20
    assert lazy.evaluated
    assert lazy._result == 20


def test_chained_eval():
    twenty = Lazy(lambda a, b: a + b, 10, 10)
    assert not twenty.evaluated
    assert twenty._result is None
    twentyfive = Lazy(lambda a, b: a + b, twenty, 5)
    assert not twentyfive.evaluated
    assert twentyfive._result is None
    result = twentyfive.evaluate()
    assert result == 25
    assert twenty.evaluated
    assert twenty._result == 20
    assert twentyfive.evaluated
    assert twentyfive._result == 25
