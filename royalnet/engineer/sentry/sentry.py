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

    def __init__(self):
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=12)
        """
        An object queue where incoming :class:`object` are stored.
        """

    def __repr__(self):
        return f"<Sentry>"

    async def f(self):
        """
        Create a :class:`.filters.Filter` object, which can be configured through its fluent interface.

        Remember to call ``.get()`` on the end of the chain to finally get the object.

        To get any object, call:

        .. code-block::

           await sentry.f().get()

        .. seealso:: :class:`.filters.Filter`

        :return: The created :class:`.filters.Filter`.
        """
        return Filter(self.queue.get)


__all__ = (
    "Sentry",
)
