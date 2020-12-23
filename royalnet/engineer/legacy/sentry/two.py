from __future__ import annotations
from royalnet.royaltyping import *
import logging
import asyncio

from .three import BoltSource

if TYPE_CHECKING:
    from .one import One


log = logging.getLogger(__name__)


InfiniteConversation = Callable[["Conversation"], Awaitable[Optional["InfiniteConversation"]]]


class Two:
    def __init__(self, sentry: "One", *, queue_size: int = 12, bolt_type: type = BoltSource):
        self.sentry: "One" = sentry
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=queue_size)
        self.bolt_type: type = bolt_type

    def __repr__(self):
        return f"<{self.__class__.__qualname__}, size {self.queue.maxsize}, emitting {self.bolt_type}>"

    def bolt(self):
        """
        Create a object of type :attr:`.bolt_type`, passing this conversation to ``__init__`` as the ``conversation``
        kwarg.

        :return: The created :class:`.wrench.ScrewSource`.
        """
        return self.bolt_type(conversation=self)

    def __call__(self):
        """
        A shortcut to call :meth:`.bolt`.
        """
        return self.bolt()

    async def put(self, item) -> None:
        """
        Put an item in the queue.

        :param item: The item to insert.

        .. seealso:: :meth:`asyncio.Queue.put`
        """
        await self.queue.put(item)


__all__ = (
    "Two",
)
