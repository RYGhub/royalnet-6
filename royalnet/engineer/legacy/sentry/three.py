from royalnet.royaltyping import *
import abc

from .. import exc

if TYPE_CHECKING:
    from .two import Two


class Three(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __len__(self):
        raise NotImplementedError()

    @abc.abstractmethod
    async def single(self):
        raise NotImplementedError()

    async def get(self):
        while True:
            try:
                return await self.single()
            except exc.Discard:
                continue

    def __await__(self):
        return self.get().__await__()

    def pipe(self, nut: Callable[[Any], Awaitable[Any]]):
        if callable(nut):
            return BoltNode(previous=self, nut=nut)
        else:
            raise TypeError("other must be either a coroutine function or a callable object")

    def __or__(self, other):
        try:
            self.pipe(other)
        except TypeError:
            raise TypeError("Right-side must be either a Nut or a coroutine function")

    @abc.abstractmethod
    def conversation(self):
        raise NotImplementedError()


class BoltSource(Three):
    def __init__(self, conversation: "Two"):
        self._conversation: "Two" = conversation
        """
        The :class:`.Conversation` whose queue will act as a source for the tree.
        """

    def __len__(self):
        return 1

    async def single(self):
        return await self._conversation.queue.get()

    def conversation(self):
        return self._conversation


class BoltNode(Three, metaclass=abc.ABCMeta):
    def __init__(self, previous: Three, nut: Callable[[Any], Awaitable[Any]]):
        self.previous: Three = previous
        """
        The previous :class:`.Bolt` in the tree.
        """

        self.nut: Callable[[Any], Awaitable[Any]] = nut
        """
        The coroutine function to apply to all objects passing through the tree.
        """

    def __len__(self):
        return len(self.previous) + 1

    async def single(self):
        return await self.nut(await self.previous.single())

    def conversation(self):
        return self.previous.conversation()


__all__ = (
    "Three",
    "BoltSource",
    "BoltNode",
)
