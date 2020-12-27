"""
Wrenches are objects which can used instead of coroutines in Sentry receiver filters,
acting similarly to function factories and allowing to easily define filter functions with parameters.
"""

from __future__ import annotations
import royalnet.royaltyping as t

import abc

from . import discard
from . import exc


class Wrench(metaclass=abc.ABCMeta):
    """
    The abstract base class for Wrenches.
    """

    @abc.abstractmethod
    async def filter(self, obj: t.Any) -> t.Any:
        """
        The function applied to all objects transiting through the pipeline:

        - If the function **returns**, its return value will be passed to the next node in the pipeline;
        - If the function **raises**, the error is propagated downwards.

        A special exception is available for discarding objects: :exc:`.discard.Discard`.
        If raised, the object will be silently ignored.
        """
        raise NotImplementedError()

    def __call__(self, obj: t.Any) -> t.Awaitable[t.Any]:
        """
        Allow instances to be directly called, emulating coroutine functions.
        """
        return self.filter(obj)


class PassAll(Wrench):
    """
    **Return** each received object as it is.

    .. note:: To be used only in testing.
    """

    async def filter(self, obj: t.Any) -> t.Any:
        return obj


class DiscardAll(Wrench):
    """
    **Discard** each received object.

    .. note:: To be used only in testing.
    """

    async def filter(self, obj: t.Any) -> t.Any:
        raise discard.Discard(obj, "Discard filter discards everything")


class ErrorAll(Wrench):
    """
    **Raise** :exc:`.exc.DeliberateException` for each received object.

    .. note:: To be used only in testing.
    """

    async def filter(self, obj: t.Any) -> t.Any:
        raise exc.DeliberateException("ErrorAll received an object")


class CheckBase(Wrench, metaclass=abc.ABCMeta):
    """
    Check a condition on the received objects:

    - If the check returns :data:`True`, the object is **returned**;
    - If the check returns :data:`False`, the object is **discarded**;
    - If an error is raised, it is **propagated**.
    """

    def __init__(self, *, invert: bool = False):
        self.invert: bool = invert
        """
        If set to :data:`True`, this Nut will invert its results:
        
        - If the check returns :data:`True`, the object is **discarded**;
        - If the check returns :data:`False`, the object is **returned**;
        - If an error is raised, it is **propagated**.
        """

    def __invert__(self):
        return self.__class__(invert=not self.invert)

    @abc.abstractmethod
    async def check(self, obj: t.Any) -> bool:
        """
        The condition to check.

        :param obj: The object passing through the pipeline.
        :return: Whether the check was successful or not.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def error(self, obj: t.Any) -> str:
        """
        The error message to attach as :attr:`.Discard.message` if the object is discarded.

        :param obj: The object passing through the pipeline.
        :return: The error message.
        """
        raise NotImplementedError()

    async def filter(self, obj: t.Any) -> t.Any:
        if await self.check(obj) ^ self.invert:
            return obj
        else:
            raise discard.Discard(obj=obj, message=self.error(obj))


class Type(CheckBase):
    """
    Check the type of an object:

    - If the object **is** of the specified type, it is **returned**;
    - If the object **isn't** of the specified type, it is **discarded**;
    """

    def __init__(self, type_: t.Type, **kwargs):
        super().__init__(**kwargs)
        self.type: t.Type = type_

    async def check(self, obj: t.Any) -> bool:
        return isinstance(obj, self.type)

    def error(self, obj: t.Any) -> str:
        return f"Not instance of type {self.type}"


class StartsWith(CheckBase):
    """
    Check if an object :func:`startswith` a certain prefix.
    """

    def __init__(self, prefix: str, **kwargs):
        super().__init__(**kwargs)
        self.prefix: str = prefix

    async def check(self, obj: t.Any) -> bool:
        return obj.startswith(self.prefix)

    def error(self, obj: t.Any) -> str:
        return f"Didn't start with {self.prefix}"


class EndsWith(CheckBase):
    """
    Check if an object :func:`endswith` a certain suffix.
    """

    def __init__(self, suffix: str, **kwargs):
        super().__init__(**kwargs)
        self.suffix: str = suffix

    async def check(self, obj: t.Any) -> bool:
        return obj.startswith(self.suffix)

    def error(self, obj: t.Any) -> str:
        return f"Didn't end with {self.suffix}"


class Choice(CheckBase):
    """
    Check if an object is among the accepted list.
    """

    def __init__(self, *accepted, **kwargs):
        super().__init__(**kwargs)
        self.accepted: t.Collection = accepted
        """
        A collection of elements which can be chosen.
        """

    async def check(self, obj: t.Any) -> bool:
        return obj in self.accepted

    def error(self, obj: t.Any) -> str:
        return f"Not a valid choice"


class RegexCheck(CheckBase):
    """
    Check if an object matches a regex pattern.
    """

    def __init__(self, pattern: t.Pattern, **kwargs):
        super().__init__(**kwargs)
        self.pattern: t.Pattern = pattern
        """
        The pattern that should be matched.
        """

    async def check(self, obj: t.Any) -> bool:
        return bool(self.pattern.match(obj))

    def error(self, obj: t.Any) -> str:
        return f"Didn't match pattern {self.pattern}"


class RegexMatch(Wrench):
    """
    Apply a regex over an object:

    - If it matches, **return** the :class:`re.Match` object;
    - If it doesn't match, **discard** the object.
    """

    def __init__(self, pattern: t.Pattern, **kwargs):
        super().__init__(**kwargs)
        self.pattern: t.Pattern = pattern
        """
        The pattern that should be matched.
        """

    async def filter(self, obj: t.Any) -> t.Any:
        if match := self.pattern.match(obj):
            return match
        else:
            raise discard.Discard(obj, f"Didn't match pattern {obj}")


class RegexReplace(Wrench):
    """
    Apply a regex over an object:

    - If it matches, replace the match(es) with :attr:`.replacement` and **return** the result.
    - If it doesn't match, **return** the object as it is.
    """

    def __init__(self, pattern: t.Pattern, replacement: t.Union[str, bytes]):
        self.pattern: t.Pattern = pattern
        """
        The pattern that should be matched.
        """

        self.replacement: t.Union[str, bytes] = replacement
        """
        The substitution string for the object.
        """

    async def filter(self, obj: t.Any) -> t.Any:
        return self.pattern.sub(self.replacement, obj)


class Lambda(Wrench):
    """
    Apply a syncronous function over the received objects.
    """

    def __init__(self, func: t.Callable[[t.Any], t.Any]):
        self.func: t.Callable[[t.Any], t.Any] = func
        """
        The function to apply.
        """

    async def filter(self, obj: t.Any) -> t.Any:
        return self.func(obj)


class Check(CheckBase):
    """
    Check a condition on the received objects.
    """

    def __init__(self, func: t.Callable[[t.Any], t.Any], error: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.func: t.Callable[[t.Any], t.Any] = func
        """
        The condition to check.
        """

        self.error: str = error
        """
        The error message to display if the check fails.
        """

    async def check(self, obj: t.Any) -> bool:
        return self.func(obj)

    def error(self, obj: t.Any) -> str:
        return self.error


__all__ = (
    "Wrench",
    "CheckBase",
    "Type",
    "StartsWith",
    "EndsWith",
    "Choice",
    "RegexCheck",
    "RegexMatch",
    "RegexReplace",
    "Lambda",
    "Check",
)
