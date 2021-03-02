from __future__ import annotations
from royalnet.royaltyping import *


Result = TypeVar("Result")


class Lazy:
    def __init__(self, obj: Callable[[Any], Result], *args, **kwargs):
        self._func: Callable[[Any], Result] = obj
        self._args = args
        self._kwargs = kwargs
        self.evaluated = False
        self._result = None

    def _evaluate_args(self) -> List[Any]:
        evaluated_args = []
        for arg in self._args:
            if isinstance(arg, Lazy):
                arg = arg.evaluate()
            evaluated_args.append(arg)
        return evaluated_args

    def _evaluate_kwargs(self) -> Dict[str, Any]:
        evaluated_kwargs = {}
        for key, value in self._kwargs.items():
            if isinstance(value, Lazy):
                value = value.evaluate()
            evaluated_kwargs[key] = value
        return evaluated_kwargs

    def evaluate(self, *args, **kwargs) -> Result:
        if not self.evaluated:
            self._result = self._func(*self._evaluate_args(), *args, **self._evaluate_kwargs(), **kwargs)
            self.evaluated = True
        return self._result

    @property
    def e(self) -> Result:
        return self.evaluate()

    @classmethod
    def decorator(cls, *args, **kwargs):
        def deco(func):
            return cls(func, *args, **kwargs)
        return deco


__all__ = (
    "Lazy",
)
