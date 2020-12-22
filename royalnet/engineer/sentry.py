from __future__ import annotations
from royalnet.royaltyping import *
import logging
import asyncio

from . import wrench

log = logging.getLogger(__name__)


class Sentry:
    """
    A class that allows using the ``await`` keyword to suspend a command execution until a new message is received.
    """

    QUEUE_SIZE = 12
    """
    The size of the object :attr:`.queue`.
    """

    def __init__(self, source_type: Type[wrench.ScrewSource] = wrench.ScrewSource):
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=self.QUEUE_SIZE)
        """
        An object queue where incoming :class:`object` are stored, with a size limit of :attr:`.QUEUE_SIZE`.
        """

        self.source_type: Type[wrench.ScrewSource] = source_type
        """
        The class to be used as source for filter trees.
        """

    def __repr__(self):
        return f"<Sentry>"

    def source(self):
        """
        Create a :class:`.wrench.ScrewSource` using the ``self.queue.get`` method as source.

        :return: The created :class:`.wrench.ScrewSource`.
        """
        return self.source_type(func=self.queue.get)

    def __call__(self, *args, **kwargs):
        return self.source()


__all__ = (
    "Sentry",
)
