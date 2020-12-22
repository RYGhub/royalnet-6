from royalnet.royaltyping import *
import abc

from .. import exc


class Wrench(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def single(self, *args, **kwargs):
        raise NotImplementedError()

    async def get(self):
        while True:
            try:
                return await self.single()
            except exc.Discard:
                continue

    def pipe(self, nut: Callable[[Any], Awaitable[Any]]):
        if callable(nut):
            return WrenchNode(previous=self, nut=nut)
        else:
            raise TypeError("other must be either a coroutine function or a callable object")

    def __or__(self, other):
        try:
            self.pipe(other)
        except TypeError:
            raise TypeError("Right-side must be either a Nut or a coroutine function")


class WrenchSource(Wrench):
    def __init__(self, func: Callable[..., Awaitable[Any]]):
        self.func: Callable[..., Awaitable[Any]] = func
        """
        The coroutine function that will act as the source for the tree.
        """

    async def single(self, *args, **kwargs):
        return await self.func(*args, **kwargs)


class WrenchNode(Wrench, metaclass=abc.ABCMeta):
    def __init__(self, previous: Wrench, nut: Callable[[Any], Awaitable[Any]]):
        self.previous: Wrench = previous
        """
        The previous node in the tree.
        """

        self.nut: Callable[[Any], Awaitable[Any]] = nut
        """
        The coroutine function to apply to all objects passing through the tree.
        """

    async def single(self, *args, **kwargs):
        return await self.nut(await self.previous.single(*args, **kwargs))
