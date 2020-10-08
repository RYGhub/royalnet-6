from royalnet.typing import *
import abc

__all__ = (
    "Challenge",
    "TrueChallenge",
)


class Challenge(metaclass=abc.ABCMeta):
    """A filter for inputs passed to a Campaign."""

    @abc.abstractmethod
    def filter(self, data: Any) -> bool:
        """Decide if the data should be skipped or not."""
        raise NotImplementedError()


class TrueChallenge(Challenge):
    """A Challenge which always returns True."""

    async def filter(self, data: Any) -> bool:
        return True
