from royalnet.royaltyping import *
import abc

from .. import exc


class Screw(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __len__(self):
        raise NotImplementedError()

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
            return ScrewNode(previous=self, nut=nut)
        else:
            raise TypeError("other must be either a coroutine function or a callable object")

    def __or__(self, other):
        try:
            self.pipe(other)
        except TypeError:
            raise TypeError("Right-side must be either a Nut or a coroutine function")


class ScrewSource(Screw):
    def __init__(self, func: Callable[..., Awaitable[Any]]):
        self.func: Callable[..., Awaitable[Any]] = func
        """
        The coroutine function that will act as the source for the tree.
        """

    def __len__(self):
        return 1

    async def single(self, *args, **kwargs):
        return await self.func(*args, **kwargs)


class ScrewNode(Screw, metaclass=abc.ABCMeta):
    def __init__(self, previous: Screw, nut: Callable[[Any], Awaitable[Any]]):
        self.previous: Screw = previous
        """
        The previous node in the tree.
        """

        self.nut: Callable[[Any], Awaitable[Any]] = nut
        """
        The coroutine function to apply to all objects passing through the tree.
        """

    def __len__(self):
        return len(self.previous) + 1

    async def single(self, *args, **kwargs):
        return await self.nut(await self.previous.single(*args, **kwargs))


__all__ = (
    "Screw",
    "ScrewSource",
    "ScrewNode",
)
