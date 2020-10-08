from royalnet.typing import *
import abc

__all__ = (
    "AsyncChallenge",
    "TrueAsyncChallenge",
)


class AsyncChallenge(metaclass=abc.ABCMeta):
    """A filter for inputs passed to an AsyncCampaign."""

    @abc.abstractmethod
    async def filter(self, data: Any) -> bool:
        """Decide if the data should be skipped or not."""
        raise NotImplementedError()


class TrueAsyncChallenge(AsyncChallenge):
    """An AsyncChallenge which always returns True."""

    async def filter(self, data: Any) -> bool:
        return True
