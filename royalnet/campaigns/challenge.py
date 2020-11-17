from royalnet.typing import *
import abc

__all__ = (
    "Challenge",
    "TrueChallenge",
)


class Challenge(metaclass=abc.ABCMeta):
    """A filter for inputs passed to a :class:`.Campaign`."""

    @abc.abstractmethod
    def filter(self, data: Any) -> bool:
        """Decide if the data should be skipped or not."""
        raise NotImplementedError()


class TrueChallenge(Challenge):
    """A :class:`.Challenge` which always returns :data:`True`."""

    async def filter(self, data: Any) -> bool:
        """Decide if the data should be skipped or not."""
        return True
