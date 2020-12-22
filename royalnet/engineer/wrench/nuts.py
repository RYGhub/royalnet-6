from royalnet.royaltyping import *
import abc
from .. import exc


class Nut(metaclass=abc.ABCMeta):
    """
    A wrapper to easily pass parameters to filter functions for :class:`royalnet.engineer.wrench.WrenchNode`.
    """

    @abc.abstractmethod
    async def filter(self, obj: Any) -> Any:
        """
        The function applied to all objects transiting through the tree:

        - If the function **returns**, its return value will be passed to the next node in the tree;
        - If the function **raises**, the error is propagated downwards.

        A special exception is available for discarding objects: :exc:`.exc.Discard`.
        If raised, :meth:`royalnet.engineer.wrench.Wrench.get` will silently ignore the object.
        """
        raise NotImplementedError()

    def __call__(self, obj: Any) -> Awaitable[Any]:
        """
        Allow instances to be directly called, emulating coroutine functions.
        """
        return self.filter(obj)


class Pass(Nut):
    """
    **Return** each received object as it is.
    """

    async def filter(self, obj: Any) -> Any:
        return obj


class Check(Nut, metaclass=abc.ABCMeta):
    """
    Check a condition on the received objects:

    - If the check returns :data:`True`, the object is **returned**;
    - If the check returns :data:`False`, the object is **discarded**;
    - If an error is raised, it is **propagated**.
    """

    def __init__(self, *, not_: bool = False):
        self.not_: bool = not_
        """
        If set to :data:`True`, this Nut will invert its results:
        
        - If the check returns :data:`True`, the object is **discarded**;
        - If the check returns :data:`False`, the object is **returned**;
        - If an error is raised, it is **propagated**.
        """

    def __invert__(self):
        return self.__class__(not_=not self.not_)

    @abc.abstractmethod
    async def check(self, obj: Any) -> bool:
        """
        The condition to check.

        :param obj: The object passing through the tree.
        :return: Whether the check was successful or not.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def error(self, obj: Any) -> str:
        """
        The error message to attach as :attr:`.exc.Discard.message` if the object is discarded.

        :param obj: The object passing through the tree.
        :return: The error message.
        """
        raise NotImplementedError()

    async def filter(self, obj: Any) -> Any:
        if await self.check(obj) ^ self.not_:
            return obj
        else:
            raise exc.Discard(obj=obj, message=self.error(obj))


class Type(Check):
    """
    Check the type of an object:
    
    - If the object **is** of the specified type, it is **returned**;
    - If the object **isn't** of the specified type, it is **discarded**;
    """

    def __init__(self, t: Type, **kwargs):
        super().__init__(**kwargs)
        self.t: Type = t

    async def check(self, obj: Any) -> bool:
        return isinstance(obj, self.t)

    def error(self, obj: Any) -> str:
        return f"Not instance of type {self.t}"


class StartsWith(Check):
    """
    Check if an object :func:`startswith` a certain prefix.
    """

    def __init__(self, prefix: str, **kwargs):
        super().__init__(**kwargs)
        self.prefix: str = prefix

    async def check(self, obj: Any) -> bool:
        return obj.startswith(self.prefix)

    def error(self, obj: Any) -> str:
        return f"Didn't start with {self.prefix}"


class EndsWith(Check):
    """
    Check if an object :func:`endswith` a certain suffix.
    """

    def __init__(self, suffix: str, **kwargs):
        super().__init__(**kwargs)
        self.suffix: str = suffix

    async def check(self, obj: Any) -> bool:
        return obj.startswith(self.suffix)

    def error(self, obj: Any) -> str:
        return f"Didn't end with {self.suffix}"


class Choice(Check):
    """
    Check if an object is among the accepted list.
    """

    def __init__(self, *accepted, **kwargs):
        super().__init__(**kwargs)
        self.accepted = accepted

    async def check(self, obj: Any) -> bool:
        return obj in self.accepted

    def error(self, obj: Any) -> str:
        return f"Not a valid choice"


class RegexCheck(Check):
    """
    Check if an object matches a regex pattern.
    """

    def __init__(self, pattern: Pattern, **kwargs):
        super().__init__(**kwargs)
        self.pattern: Pattern = pattern

    async def check(self, obj: Any) -> bool:
        return bool(self.pattern.match(obj))

    def error(self, obj: Any) -> str:
        return f"Didn't match pattern {self.pattern}"


__all__ = (
    "Nut",
    "Pass",
    "Check",
    "Type",
    "StartsWith",
    "EndsWith",
    "Choice",
    "RegexCheck",
)
