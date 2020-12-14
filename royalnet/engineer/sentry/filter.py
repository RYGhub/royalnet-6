"""
.. note:: I'm not sure about this module. It doesn't seem to be really pythonic. It will probably be deprecated in the
          future...
"""

from __future__ import annotations
from royalnet.royaltyping import *
import functools
import logging

from engineer import exc, blueprints

log = logging.getLogger(__name__)


class Filter:
    """
    A fluent interface for filtering data.
    """

    def __init__(self, func: Callable):
        self.func: Callable = func

    async def get(self) -> Any:
        """
        Wait until an :class:`object` leaves the queue and passes through the filter, then return it.

        :return: The :class:`object` which entered the queue.
        """
        while True:
            try:
                result = await self.func(None)
            except exc.Discard as e:
                log.debug(str(e))
                continue
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

        .. seealso:: :meth:`._deco_filter`, :func:`filter`

        :param c: A function that takes in input an object and performs a check on it, returning either :data:`True`
                  or :data:`False`.
        :param error: The reason for which objects should be discarded.
        :return: A new :class:`Filter` with this new condition.
        """
        return self.__class__(self._deco_filter(c, error=error)(self.func))

    @staticmethod
    def _deco_map(c: Callable[[Any], object]):
        """
        A decorator which applies the function ``c`` on all objects transiting through the queue:
        - If the function **returns**, return its return value;
        - If the function **raises** an error, it is propagated upwards.

        .. seealso:: :func:`map`

        :param c: A function that takes in input an enqueued object and returns either the same object or something
                  else.
        """
        def decorator(func):
            @functools.wraps(func)
            async def decorated(obj):
                result: Any = await func(obj)
                return c(result)
            return decorated
        return decorator

    def map(self, c: Callable[[Any], bool]) -> Filter:
        """
        Apply the function ``c`` on all objects transiting through the queue:
        - If the function **returns**, its return value replaces the object in the queue;
        - If the function **raises** :exc:`.exc.Discard`, the object is discarded;
        - If the function **raises another error**, propagate the error upwards.

        .. seealso:: :meth:`._deco_map`, :func:`filter`

        :param c: A function that takes in input an enqueued object and returns either the same object or something
                  else.
        :return: A new :class:`Filter` with this new condition.
        """
        return self.__class__(self._deco_map(c)(self.func))

    def type(self, t: type) -> Filter:
        """
        Check if an object passing through the queue :func:`isinstance` of the type ``t``.

        :param t: The type that objects should be instances of.
        :return: A new :class:`Filter` with this new condition.
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
        - If the :class:`.blueprints.Blueprint` doesn't have data for at least one of the fields, the object is
          discarded;
        - the :class:`.blueprints.Blueprint` never has data for at least one of the fields,
          :exc:`.exc.NotAvailableError` is propagated upwards.

        :param fields: The fields to test for.
        :param propagate_not_available: If :exc:`.exc.NotAvailableError` should be propagated
                                        instead of discarding the errored object.
        :param propagate_never_available: If :exc:`.exc.NeverAvailableError` should be propagated
                                          instead of discarding the errored object.
        :return: A new :class:`Filter` with this new condition.
        """
        def check(obj):
            try:
                return obj.requires(*fields)
            except exc.NotAvailableError:
                if not propagate_not_available:
                    raise
                raise exc.Discard(obj, "Data is not available")
            except exc.NeverAvailableError:
                if not propagate_never_available:
                    raise
                raise exc.Discard(obj, "Data is never available")

        return self.filter(check, error=".requires() method returned False")

    def field(self) -> Filter:
        """
        # TODO

        :return: A new :class:`Filter` with the new requirements.
        """
        return self.requires(blueprints.Message.text).map(lambda o: o.text())

    @staticmethod
    def _deco_startswith(prefix: str):
        def decorator(func):
            @functools.wraps(func)
            def decorated(obj):
                result: str = func(obj)
                if not result.startswith(prefix):
                    raise exc.Discard(result, f"Text didn't start with {prefix}")
                return result
            return decorated
        return decorator

    def startswith(self, prefix: str):
        """
        Check if an object starts with the specified prefix and discard the objects that do not.

        :param prefix: The prefix object should start with.
        :return: A new :class:`Filter` with the new requirements.
        """
        return self.__class__(self._deco_startswith(prefix)(self.func))

    @staticmethod
    def _deco_regex(pattern: Pattern):
        def decorator(func):
            @functools.wraps(func)
            def decorated(obj):
                result: str = func(obj)
                if match := pattern.match(result):
                    return match
                else:
                    raise exc.Discard(result, f"Text didn't match pattern {pattern}")
            return decorated
        return decorator

    def regex(self, pattern: Pattern):
        """
        Apply a regex over an object and discard the object if it does not match.

        :param pattern: The pattern that should be matched by the text.
        :return: A new :class:`Filter` with the new requirements.
        """
        return self.__class__(self._deco_regex(pattern)(self.func))

    def choices(self, *choices):
        """
        Ensure an object is in the ``choices`` list, discarding the object otherwise.

        :param choices: The pattern that should be matched by the text.
        :return: A new :class:`Filter` with the new requirements.
        """
        return self.__class__(self._deco_check(lambda o: o in choices, error="Not a valid choice")(self.func))


__all__ = (
    "Filter",
)
