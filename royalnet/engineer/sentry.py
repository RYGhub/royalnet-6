"""
This module contains the :class:`.Sentry` class and its descendents :class:`SentryFilter` and :class:`SentrySource`\\ .


They support event filtering through Wrenches and coroutine functions.
"""

from __future__ import annotations
import royalnet.royaltyping as t

import abc
import logging
import asyncio

from . import discard

if t.TYPE_CHECKING:
    from .dispenser import Dispenser
    from .bullet import Projectile

log = logging.getLogger(__name__)


class Sentry(metaclass=abc.ABCMeta):
    """
    A :class:`.Sentry` is an asynchronous receiver for :class:`~royalnet.engineer.bullet.projectiles._base.Projectile`
    incoming from :class:`~royalnet.engineer.dispenser.Dispenser`\\ s.

    Sentries can be chained together to form a filtering pipeline, starting with a :class:`.SentrySource` followed by
    zero or more :class:`.SentryFilter`\\ s.

    This abstract base class represents a single node of the pipeline.
    """

    @abc.abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_nowait(self):
        """
        Try to get a single :class:`~royalnet.engineer.bullet.projectiles._base.Projectile` from the pipeline,
        **without blocking** or **handling :class:`~royalnet.engineer.discard.Discard`\\ s** .

        :return: The **returned** :class:`~royalnet.engineer.bullet.projectiles._base.Projectile`.

        :raises asyncio.QueueEmpty: If the queue is empty.
        :raises .discard.Discard: If the object was **:class:`~royalnet.engineer.discard.Discard`\\ ed** by
                                  the pipeline.
        :raises Exception: If an exception was **raised** in the pipeline.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    async def get(self):
        """
        Try to get a single :class:`~royalnet.engineer.bullet.projectiles._base.Projectile` from the pipeline,
        **blocking** until something is available, but
        **without handling :class:`~royalnet.engineer.discard.Discard`\\ s**.

        :return: The **returned** :class:`~royalnet.engineer.bullet.projectiles._base.Projectile`.

        :raises .discard.Discard: If the object was **discarded** by the pipeline.
        :raises Exception: If an exception was **raised** in the pipeline.
        """
        raise NotImplementedError()

    async def wait(self):
        """
        Try to get a single :class:`~.bullet.Projectile` from the pipeline, **blocking** until something is available
        and is **not discarded**.

        :return: The **returned** :class:`~.bullet.Projectile`.

        :raises Exception: If an exception was **raised** in the pipeline.
        """
        while True:
            try:
                result = await self.get()
                log.debug(f"Returned: {result}")
                return result
            except discard.Discard as d:
                log.debug(f"{str(d)}")
                continue

    def __await__(self):
        """
        Awaiting an object implementing :class:`.Sentry` corresponds to awaiting :meth:`.wait`.
        """
        return self.get().__await__()

    @abc.abstractmethod
    async def put(self, item: "Projectile") -> None:
        """
        Insert a new item in the queue.

        :param item: The item to be added.
        """
        raise NotImplementedError()

    def filter(self, wrench: t.WrenchLike) -> SentryFilter:
        """
        Chain a new filter to the pipeline.

        :param wrench: The filter to add to the chain. It can either be a :class:`~royalnet.engineer.wrench.Wrench`,
                       or a coroutine function accepting a single object as parameter and returning another one.
        :return: The resulting :class:`.SentryFilter`\\ .
        :raises TypeError: If the right side operator is neither a :class:`~royalnet.engineer.wrench.Wrench` or a
                           coroutine function.

        .. seealso:: :meth:`.__or__`
        """
        if callable(wrench):
            return SentryFilter(previous=self, wrench=wrench)
        else:
            raise TypeError("wrench must be either a Wrench or a coroutine function")

    def __or__(self, other: t.WrenchLike) -> SentryFilter:
        """
        A unix-pipe-like interface for :meth:`.filter`.

        .. code-block::

           await (sentry | wrench.Type(engi.MessageReceived) | wrench.Lambda(lambda o: o.text))

        :return: The resulting :class:`.SentryFilter`\\ .
        :raises TypeError: If the right side operator is neither a :class:`~royalnet.engineer.wrench.Wrench` or a
                           coroutine function.
        """
        try:
            return self.filter(other)
        except TypeError:
            raise TypeError("Right-side must be either a Wrench or a coroutine function")

    @abc.abstractmethod
    def dispenser(self) -> Dispenser:
        """
        Get the :class:`~royalnet.engineer.dispenser.Dispenser` that created this :class:`.Sentry`.

        :return: The :class:`~royalnet.engineer.dispenser.Dispenser` object.
        """
        raise NotImplementedError()


class SentryFilter(Sentry):
    """
    A non-root node of the filtering pipeline.
    """

    def __init__(self, previous: Sentry, wrench: t.WrenchLike):
        self.previous: Sentry = previous
        """
        The previous node of the pipeline.
        """

        self.wrench: t.WrenchLike = wrench
        """
        The coroutine function to apply to all objects passing through this node.
        """

    def __len__(self) -> int:
        return len(self.previous) + 1

    def get_nowait(self):
        return self.previous.get_nowait()

    async def get(self):
        return await self.previous.get()

    async def put(self, item) -> None:
        return await self.previous.put(item)

    def dispenser(self) -> Dispenser:
        return self.previous.dispenser()


class SentrySource(Sentry):
    """
    The root and source of the pipeline.
    """

    def __init__(self, dispenser: "Dispenser", queue_size: int = 12):
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=queue_size)
        self._dispenser: "Dispenser" = dispenser

    def __len__(self) -> int:
        return 1

    def get_nowait(self):
        return self.queue.get_nowait()

    async def get(self):
        return await self.queue.get()

    async def put(self, item) -> None:
        return await self.queue.put(item)

    def dispenser(self) -> Dispenser:
        return self._dispenser


__all__ = (
    "Sentry",
    "SentryFilter",
    "SentrySource",
)
