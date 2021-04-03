"""
Dispensers instantiate sentries and dispatch events in bulk to the whole group.
"""

from __future__ import annotations
import royalnet.royaltyping as t

import logging
import contextlib

from .sentry import SentrySource
from .conversation import Conversation
from .exc import LockedDispenserError
from .bullet.projectiles import Projectile

log = logging.getLogger(__name__)


class Dispenser:
    def __init__(self):
        self.sentries: t.List[SentrySource] = []
        """
        A :class:`list` of all the running sentries of this dispenser.
        """

        self._locked_by: t.List[Conversation] = []
        """
        The conversation that are currently locking this dispenser.
        
        .. seealso:: :meth:`.lock`
        """

    async def put(self, item: Projectile) -> None:
        """
        Insert a new projectile in the queues of all the running sentries.

        :param item: The projectile to insert.
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
        :raises .LockedDispenserError: If the dispenser is currently :attr:`.locked_by` a :class:`.Conversation`.
        """
        log.debug(f"Trying to run: {conv!r}")

        if self._locked_by:
            log.debug(f"Dispenser is locked by {self._locked_by!r}, refusing to run {conv!r}")
            raise LockedDispenserError(self._locked_by, f"The Dispenser is currently locked by {self._locked_by!r} and "
                                                        f"cannot start new conversations.")

        log.debug(f"Running: {conv}")
        with self.sentry() as sentry:
            state = conv(_sentry=sentry, **kwargs)

            log.debug(f"First state: {state}")
            while state := await state:
                log.debug(f"Switched to: {state}")

    @contextlib.contextmanager
    def lock(self, conv: Conversation):
        """
        Lock the dispenser while this :func:`~contextlib.contextmanager` is in scope.

        A locked dispenser will refuse to :meth:`.run` any new conversations, raising :exc:`.exc.LockedDispenserError`
        instead.

        :param conv: The conversation that requested the lock.

        .. seealso:: :attr:`._locked_by`
        """
        log.debug(f"Adding lock: {conv!r}")
        self._locked_by.append(conv)

        try:
            yield
        finally:
            log.debug(f"Clearing lock: {conv!r}")
            self._locked_by.remove(conv)


__all__ = (
    "Dispenser",
)
