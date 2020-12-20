from __future__ import annotations
from royalnet.royaltyping import *
import functools
import logging
import abc

from .. import exc, blueprints

log = logging.getLogger(__name__)


class Wrench(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def single(self):
        raise NotImplementedError()

    async def get(self):
        while True:
            try:
                return await self.single()
            except exc.Discard:
                continue


class WrenchSource(Wrench):
    def __init__(self, func: Callable[..., Awaitable[Any]]):
        self.func: Callable[..., Awaitable[Any]] = func
        """
        The coroutine that will act as the source for the filter tree.
        """

    async def single(self):
        return await self.func()


class WrenchFilter(Wrench, metaclass=abc.ABCMeta):
    def __init__(self, previous: Wrench):
        self.previous: Wrench = previous
        """
        The previous node in the tree.
        """

    @abc.abstractmethod
    async def filter(self, obj: Any) -> Any:
        raise NotImplementedError()

    async def single(self):
        return await self.filter(await self.previous.single())


class FilterNode:
    def __init__(self, *,
                 func: Optional[Callable[..., Awaitable[Any]]] = None,
                 previous: Optional[FilterNode] = None):
        self.func: Optional[Callable[[...], Awaitable[Any]]] = func

        self.previous: Optional[FilterNode] = previous

    def __len__(self):
        """
        :return: The depth of this node in the filter tree.

        The source node has depth 0.
        """
        if self.func:
            return 0
        return len(self.previous) + 1

    def __repr__(self):
        if self.func:
            return f"{self.__class__.__qualname__}(func={repr(self.func)})"

        return f"{self.__class__.__qualname__}(previous={repr(self.previous)})"

    def is_valid(self):
        return not (self.func is None and self.previous is None)

    async def single(self, *args, **kwargs):
        """
        Let a single :class:`object` pass through the filter, then either return it or raise an error if the object was
        filtered.

        :param args: Positional arguments to pass to the :attr:`.func`.
        :param kwargs: Keyworded arguments to pass to the :attr:`.func`.
        :return: The :class:`object` which passed through the filter tree.
        :raises exc.Discard: If the :class:`object` was filtered at some point of the tree.
        """
        try:
            if self.func:
                result = await self.func(*args, **kwargs)
            elif self.previous:
                result = await self.previous.single(*args, **kwargs)
        except exc.Discard as e:
            log.debug(str(e))
            raise
        else:
            log.debug(f"Dequeued {result}")
            return result



class Filter:
    """
    A fluent interface for filtering data.
    """

    def __init__(self, func: Callable):
        self.func: Callable = func

    async def get(self) -> Any:
        """
        Wait until an :class:`object` leaves the queue and passes through the filter, then return it.

        :return: The :class:`object` which left the queue.
        """
        while True:
            try:
                return await self.get_single()
            except exc.Discard:
                continue

    async def get_single(self) -> Any:
        """
        Let one :class:`object` pass through the filter, then either return it or raise an error if the object should be
        discarded.

        :return: The :class:`object` which left the queue.
        :raises exc.Discard: If the object was filtered.
        """
        try:
            result = await self.func(None)
        except exc.Discard as e:
            log.debug(str(e))
            raise
        else:
            log.debug(f"Dequeued {result}")
            return result

    @staticmethod
    def _deco_filter(c: Callable[[Any], bool], *, error: str):
        """
        A decorator which checks the condition ``c`` on all objects transiting through the queue:

        - If the check **passes**, the object itself is returned;
        - If the check **fails**, :exc:`.exc.Discard` is raised, with the object and the ``error`` string as parameters;
        - If an error is raised, propagate the error upwards.

        .. warning:: Raising :exc:`.exc.Discard` in ``c`` will automatically cause the object to be discarded, as if
                     :data:`False` was returned.

        :param c: A function that takes in input an enqueued object and returns either the same object or a new one to
                  pass to the next filter in the queue.
        :param error: The string that :exc:`.exc.Discard` should display if the object is discarded.
        """
        def decorator(func):
            @functools.wraps(func)
            async def decorated(obj):
                result: Any = await func(obj)
                if c(result):
                    return result
                else:
                    raise exc.Discard(obj=result, message=error)
            return decorated
        return decorator

    def filter(self, c: Callable[[Any], bool], error: str) -> Filter:
        """
        Check the condition ``c`` on all objects transiting through the queue:

        - If the check **passes**, the object goes on to the next filter;
        - If the check **fails**, the object is discarded, with ``error`` as reason;
        - If an error is raised, propagate the error upwards.

        :param c: A function that takes in input an object and performs a check on it, returning either :data:`True`
                  or :data:`False`.
        :param error: The reason for which objects should be discarded.
        :return: A new :class:`Filter` with this new condition.

        .. seealso:: :meth:`._deco_filter`, :func:`filter`
        """
        return self.__class__(self._deco_filter(c, error=error)(self.func))

    @staticmethod
    def _deco_map(c: Callable[[Any], object]):
        """
        A decorator which applies the function ``c`` on all objects transiting through the queue:

        - If the function **returns**, return its return value;
        - If the function **raises** an error, it is propagated upwards.

        :param c: A function that takes in input an enqueued object and returns either the same object or something
                  else.

        .. seealso:: :func:`map`
        """
        def decorator(func):
            @functools.wraps(func)
            async def decorated(obj):
                result: Any = await func(obj)
                return c(result)
            return decorated
        return decorator

    def map(self, c: Callable[[Any], object]) -> Filter:
        """
        Apply the function ``c`` on all objects transiting through the queue:

        - If the function **returns**, its return value replaces the object in the queue;
        - If the function **raises** :exc:`.exc.Discard`, the object is discarded;
        - If the function **raises another error**, propagate the error upwards.

        :param c: A function that takes in input an enqueued object and returns either the same object or something
                  else.
        :return: A new :class:`Filter` with this new condition.

        .. seealso:: :meth:`._deco_map`, :func:`filter`
        """
        return self.__class__(self._deco_map(c)(self.func))

    def type(self, t: type) -> Filter:
        """
        Check if an object passing through the queue :func:`isinstance` of the type ``t``.

        :param t: The type that objects should be instances of.
        :return: A new :class:`Filter` with this new condition.

        .. seealso:: :func:`isinstance`
        """
        return self.filter(lambda o: isinstance(o, t), error=f"Not instance of type {t}")

    def msg(self) -> Filter:
        """
        Check if an object passing through the queue :func:`isinstance` of :class:`.blueprints.Message`.

        :return: A new :class:`Filter` with this new condition.
        """
        return self.type(blueprints.Message)

    def requires(self, *fields,
                 propagate_not_available=False,
                 propagate_never_available=True) -> Filter:
        """
        Test a :class:`.blueprints.Blueprint`'s fields by using its ``.requires()`` method:

        - If the :class:`.blueprints.Blueprint` has the appropriate fields, return it;
        - If the :class:`.blueprints.Blueprint` doesn't have data for at least one of the fields, the object is discarded;
        - the :class:`.blueprints.Blueprint` never has data for at least one of the fields, :exc:`.exc.NotAvailableError` is propagated upwards.

        :param fields: The fields to test for.
        :param propagate_not_available: If :exc:`.exc.NotAvailableError` should be propagated
                                        instead of discarding the errored object.
        :param propagate_never_available: If :exc:`.exc.NeverAvailableError` should be propagated
                                          instead of discarding the errored object.
        :return: A new :class:`Filter` with this new condition.

        .. seealso:: :meth:`.blueprints.Blueprint.requires`
        """
        def check(obj):
            try:
                return obj.requires(*fields)
            except exc.NotAvailableError:
                if propagate_not_available:
                    raise
                raise exc.Discard(obj, "Data is not available")
            except exc.NeverAvailableError:
                if propagate_never_available:
                    raise
                raise exc.Discard(obj, "Data is never available")

        return self.filter(check, error=".requires() method returned False")

    def field(self, field: str,
              propagate_not_available=False,
              propagate_never_available=True) -> Filter:
        """
        Replace a :class:`.blueprints.Blueprint` with the value of one of its fields.

        :param field: The field to access.
        :param propagate_not_available: If :exc:`.exc.NotAvailableError` should be propagated
                                        instead of discarding the errored object.
        :param propagate_never_available: If :exc:`.exc.NeverAvailableError` should be propagated
                                          instead of discarding the errored object.
        :return: A new :class:`Filter` with the new requirements.
        """
        def replace(obj):
            try:
                return obj.__getattribute__(field)()
            except exc.NotAvailableError:
                if propagate_not_available:
                    raise
                raise exc.Discard(obj, "Data is not available")
            except exc.NeverAvailableError:
                if propagate_never_available:
                    raise
                raise exc.Discard(obj, "Data is never available")

        return self.map(replace)

    def startswith(self, prefix: str):
        """
        Check if an object starts with the specified prefix and discard the objects that do not.

        :param prefix: The prefix object should start with.
        :return: A new :class:`Filter` with the new requirements.

        .. seealso:: :meth:`str.startswith`
        """
        return self.filter(lambda x: x.startswith(prefix), error=f"Text didn't start with {prefix}")

    def endswith(self, suffix: str):
        """
        Check if an object ends with the specified suffix and discard the objects that do not.

        :param suffix: The prefix object should start with.
        :return: A new :class:`Filter` with the new requirements.

        .. seealso:: :meth:`str.endswith`
        """
        return self.filter(lambda x: x.endswith(suffix), error=f"Text didn't end with {suffix}")

    def regex(self, pattern: Pattern):
        """
        Apply a regex over an object and discard the object if it does not match.

        :param pattern: The pattern that should be matched by the text.
        :return: A new :class:`Filter` with the new requirements.
        """
        def mapping(x):
            if match := pattern.match(x):
                return match
            else:
                raise exc.Discard(x, f"Text didn't match pattern {pattern}")

        return self.map(mapping)

    def choices(self, *choices):
        """
        Ensure an object is in the ``choices`` list, discarding the object otherwise.

        :param choices: The pattern that should be matched by the text.
        :return: A new :class:`Filter` with the new requirements.
        """
        return self.filter(lambda o: o in choices, error="Not a valid choice")


__all__ = (
    "Filter",
)
