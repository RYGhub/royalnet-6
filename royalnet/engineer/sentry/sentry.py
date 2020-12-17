from __future__ import annotations
from royalnet.royaltyping import *
import logging
import asyncio

from .filter import Filter

log = logging.getLogger(__name__)


class Sentry:
    """
    A class that allows using the ``await`` keyword to suspend a command execution until a new message is received.
    """

    QUEUE_SIZE = 12
    """
    The size of the object :attr:`.queue`.
    """

    def __init__(self, filter_type: Type[Filter] = Filter):
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=self.QUEUE_SIZE)
        """
        An object queue where incoming :class:`object` are stored, with a size limit of :attr:`.QUEUE_SIZE`.
        """

        self.filter_type: Type[Filter] = filter_type
        """
        The filter to be used in :meth:`.f` calls, by default :class:`.filters.Filter`.
        """

    def __repr__(self):
        return f"<Sentry>"

    def f(self):
        """
        Create a :attr:`.filter_type` object, which can be configured through its fluent interface.

        Remember to call ``.get()`` on the end of the chain to finally get the object.

        To get any object, call:

        .. code-block::

           await sentry.f().get()

        .. seealso:: :class:`.filters.Filter`

        :return: The created :class:`.filters.Filter`.
        """
        async def func(_):
            return await self.queue.get()
        return self.filter_type(func)


__all__ = (
    "Sentry",
)
