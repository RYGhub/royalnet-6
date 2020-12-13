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
    def _deco_type(t: type):
        def decorator(func):
            @functools.wraps(func)
            def decorated(obj):
                result: Any = func(obj)
                if not isinstance(result, t):
                    raise exc.Discard(result, f"Not instance of type {t}")
                return result
            return decorated
        return decorator

    def type(self, t: type) -> Filter:
        """
        :exc:`exc.Discard` all objects that are not an instance of ``t``.

        :param t: The type that objects should be instances of.
        :return: A new :class:`Filter` with the new requirements.
        """
        return self.__class__(self._deco_type(t)(self.func))

    def msg(self) -> Filter:
        """
        :exc:`exc.Discard` all objects that are not an instance of :class:`.blueprints.Message`.

        :return: A new :class:`Filter` with the new requirements.
        """
        return self.__class__(self._deco_type(blueprints.Message)(self.func))

    @staticmethod
    def _deco_requires(*fields):
        def decorator(func):
            @functools.wraps(func)
            def decorated(obj):
                result: blueprints.Blueprint = func(obj)
                try:
                    result.requires(*fields)
                except exc.NotAvailableError:
                    raise exc.Discard(result, "Missing data")
                except AttributeError:
                    raise exc.Discard(result, "Missing .requires() method")
                return result
            return decorated
        return decorator

    def requires(self, *fields) -> Filter:
        """
        Test an object's fields by using its ``.requires()`` method (expecting it to be
        :meth:`.blueprints.Blueprint.requires`) and discard everything that does not pass the check.

        :param fields: The fields to test for.
        :return: A new :class:`Filter` with the new requirements.
        """
        return self.__class__(self._deco_requires(*fields)(self.func))

    @staticmethod
    def _deco_text():
        def decorator(func):
            @functools.wraps(func)
            def decorated(obj):
                result: blueprints.Message = func(obj)
                try:
                    text = result.text()
                except exc.NotAvailableError:
                    raise exc.Discard(result, "No text")
                except AttributeError:
                    raise exc.Discard(result, "Missing text method")
                return text
            return decorated
        return decorator

    def text(self) -> Filter:
        """
        Get the text of the passed object by using its ``.text()`` method (expecting it to be
        :meth:`.blueprints.Message.text`), while discarding all objects that don't have a text.

        :return: A new :class:`Filter` with the new requirements.
        """
        return self.__class__(self._deco_text()(self.func))

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
        Apply a regex over an object's text (obtained through its ``.text()`` method, expecting it to be
        :meth:`.blueprints.Message.text`) and discard the object if it does not match.

        :param pattern: The pattern that should be matched by the text.
        :return: A new :class:`Filter` with the new requirements.
        """
        return self.__class__(self._deco_regex(pattern)(self.func))

    @staticmethod
    def _deco_choices(*choices):
        def decorator(func):
            @functools.wraps(func)
            def decorated(obj: blueprints.Message):
                result = func(obj)
                if result not in choices:
                    raise exc.Discard(result, "Not a valid choice")
                return result
            return decorated
        return decorator

    def choices(self, *choices):
        """
        Ensure an object is in the ``choices`` list, discarding the object otherwise.

        :param choices: The pattern that should be matched by the text.
        :return: A new :class:`Filter` with the new requirements.
        """
        return self.__class__(self._deco_choices(*choices)(self.func))


__all__ = (
    "Filter",
)
