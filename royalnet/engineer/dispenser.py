"""
This module contains the :class:`.Dispenser` class.
"""

from __future__ import annotations
import royalnet.royaltyping as t

import logging
import contextlib

from .sentry import SentrySource
from .exc import EngineerException
from .bullet.projectiles import Projectile

log = logging.getLogger(__name__)


class DispenserException(EngineerException):
    """
    The base class for errors in :mod:`royalnet.engineer.dispenser`\\ .
    """


class LockedDispenserError(DispenserException):
    """
    The :class:`.Dispenser` couldn't start a new :class:`~royalnet.engineer.conversation.Conversation` as it is
    currently :attr:`.Dispenser.lock`\\ ed.
    """
    def __init__(self, locked_by, *args):
        super().__init__(*args)
        self.locked_by = locked_by


class Dispenser:
    """
    A :class:`.Dispenser` is an object which instantiates multiple :class:`~royalnet.engineer.sentry.Sentry` and
    multiplexes and distributes incoming :class:`~royalnet.engineer.bullet.projectiles._base.Projectile`\\ s to them.

    They usually represent a single "conversation channel" with the bot: either a chat channel, or an user.
    """

    def __init__(self):
        self.sentries: t.List[SentrySource] = []
        """
        A :class:`list` of all the running sentries of this dispenser.
        """

        self.locked_by: t.List[t.ConversationProtocol] = []
        """
        The conversation that is currently locking this dispenser.
        
        .. seealso:: :meth:`.lock`
        """

    async def put(self, item: Projectile) -> None:
        """
        Insert a new :class:`~royalnet.engineer.bullet.projectiles._base.Projectile` in the queues of all the
        running :attr:`.sentries`.

        :param item: The :class:`~royalnet.engineer.bullet.projectiles._base.Projectile` to insert.
        """
        log.debug(f"Putting {item!r}...")
        for sentry in self.sentries:
            await sentry.put(item)

    @contextlib.contextmanager
    def sentry(self, *args, **kwargs):
        """
        A :func:`~contextlib.contextmanager` which creates a :class:`.SentrySource` and keeps it in :attr:`.sentries`
        while it is being used.
        """
        log.debug("Creating a new SentrySource...")
        sentry = SentrySource(dispenser=self, *args, **kwargs)

        log.debug(f"Adding: {sentry!r}")
        self.sentries.append(sentry)

        log.debug(f"Yielding: {sentry!r}")
        yield sentry

        log.debug(f"Removing from the sentries list: {sentry!r}")
        self.sentries.remove(sentry)

    async def run(self, conv: t.ConversationProtocol, **kwargs) -> None:
        """
        Run a :class:`~royalnet.engineer.conversation.Conversation`\\ .

        :param conv: The :class:`~royalnet.engineer.conversation.Conversation` to run.
        :raises .LockedDispenserError: If the dispenser is currently :attr:`.locked_by` a :class:`.Conversation`.
        """
        log.debug(f"Trying to run: {conv!r}")

        if self.locked_by:
            log.debug(f"Dispenser is locked by {self.locked_by!r}, refusing to run {conv!r}")
            raise LockedDispenserError(
                f"The Dispenser is currently locked and cannot start any new Conversation.", self.locked_by)

        log.debug(f"Running: {conv!r}")
        with self.sentry() as sentry:
            await conv(_sentry=sentry, **kwargs)

    @contextlib.contextmanager
    def lock(self, conv: t.ConversationProtocol):
        """
        Lock the :class:`.Dispenser` while this :func:`~contextlib.contextmanager` is in scope.

        A locked :class:`.Dispenser` will refuse to :meth:`.run` any new conversations,
        raising :exc:`.LockedDispenserError` instead.

        :param conv: The conversation that requested the lock.

        .. seealso:: :attr:`.locked_by`
        """
        log.debug(f"Adding lock: {conv!r}")
        self.locked_by.append(conv)

        try:
            yield
        finally:
            log.debug(f"Clearing lock: {conv!r}")
            self.locked_by.remove(conv)


__all__ = (
    "Dispenser",
    "DispenserException",
    "LockedDispenserError",
)
