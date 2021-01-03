"""
Dispensers instantiate sentries and dispatch events in bulk to the whole group.
"""

from __future__ import annotations
import royalnet.royaltyping as t

import logging
import contextlib

from .sentry import SentrySource
from .conversation import Conversation

log = logging.getLogger(__name__)


class Dispenser:
    def __init__(self):
        self.sentries: t.List[SentrySource] = []
        """
        A :class:`list` of all the running sentries of this dispenser.
        """

    async def put(self, item: t.Any) -> None:
        """
        Insert a new item in the queues of all the running sentries.

        :param item: The item to insert.
        """
        log.debug(f"Putting {item}...")
        for sentry in self.sentries:
            await sentry.put(item)

    @contextlib.contextmanager
    def sentry(self, *args, **kwargs):
        """
        A context manager which creates a :class:`.SentrySource` and keeps it in :attr:`.sentries` while it is being
        used.
        """
        log.debug("Creating a new SentrySource...")
        sentry = SentrySource(dispenser=self, *args, **kwargs)

        log.debug(f"Adding: {sentry}")
        self.sentries.append(sentry)

        log.debug(f"Yielding: {sentry}")
        yield sentry

        log.debug(f"Removing from the sentries list: {sentry}")
        self.sentries.remove(sentry)

    async def run(self, conv: Conversation, **kwargs) -> None:
        """
        Run the passed conversation.

        :param conv: The conversation to run.
        """
        log.debug(f"Running: {conv}")
        with self.sentry() as sentry:
            state = conv(_sentry=sentry, **kwargs)

            log.debug(f"First state: {state}")
            while state := await state:
                log.debug(f"Switched to: {state}")


__all__ = (
    "Dispenser",
)
