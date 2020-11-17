from __future__ import annotations
from royalnet.typing import *
import logging
import inspect
import datetime
from .asyncchallenge import AsyncChallenge, TrueAsyncChallenge
from .exc import *
log = logging.getLogger(__name__)

__all__ = (
    "AsyncCampaign",
)


class AsyncCampaign:
    """
    The AsyncCampaign module allows for branching asyncgenerator-based back-and-forths between the software and the
    user.

    An :class:`.AsyncCampaign` consists of multiple chained AsyncAdventures, which are AsyncGenerators yielding tuples
    with an
    AsyncChallenge and optional data.
    """
    def __init__(self, start: AsyncAdventure, challenge: Optional[AsyncChallenge], *args, **kwargs):
        """
        Initialize an :class:`.AsyncCampaign` object.

        .. warning:: Do not use this, use the :meth:`.create()` method instead!

        :param start: The starting adventure for the :class:`.AsyncCampaign`.
        """
        self.adventure: AsyncAdventure = start
        self.challenge: AsyncChallenge = challenge or TrueAsyncChallenge()
        self.last_update: datetime.datetime = ...

    @classmethod
    async def create(cls, start: AsyncAdventure, challenge: Optional[AsyncChallenge] = None, *args, **kwargs) -> AsyncCampaign:
        """
        Create a new :class:`.AsyncCampaign` object.

        :param start: The starting Adventure for the :class:`.AsyncCampaign`.
        :param challenge: The AsyncChallenge the campaign should start with.
        :return: The created :class:`.AsyncCampaign`.
        """
        campaign = cls(start=start, challenge=challenge, *args, **kwargs)
        await campaign._asend(None)
        return campaign

    async def _asend(self, data: Any) -> Any:
        try:
            return await self.adventure.asend(data)
        except RuntimeError:
            log.error(f"{self.adventure} is being used unexpectedly by something else!")
            raise

    async def _athrow(self, typ: Type[BaseException], val: Optional[BaseException], tb: Any) -> Any:
        try:
            return await self.adventure.athrow(typ, val, tb)
        except RuntimeError:
            log.error(f"{self.adventure} is being used unexpectedly by something else!")
            raise

    async def _aclose(self) -> None:
        try:
            await self.adventure.aclose()
        except RuntimeError:
            log.error(f"{self.adventure} is being used unexpectedly by something else!")
            raise

    async def next(self, data: Any = None) -> List:
        """
        Try to advance the :class:`.AsyncCampaign` with the passed data.

        :param data: The data to pass to the current AsyncAdventure.
        :return: Optional additional data returned by the AsyncAdventure.
        :raises ChallengeFailedError: if the data passed fails the AsyncChallenge check.
        """
        self.last_update = datetime.datetime.now()
        if not await self.challenge.filter(data):
            raise ChallengeFailedError(f"{data} failed the {self.challenge} challenge")
        result = await self._asend(data)
        if inspect.isasyncgen(result):
            await self._aclose()
            self.adventure = result
            await self._asend(None)
            return await self.next(data)
        elif isinstance(result, AsyncChallenge):
            self.challenge = result
            return []
        elif result is None:
            return []
        elif isinstance(result, tuple) and len(result) > 0:
            if isinstance(result[0], AsyncChallenge):
                self.challenge, *output = result
                return output
            elif result[0] is None:
                _, *output = result
                return output
        else:
            raise TypeError(f"AsyncAdventure yielded an invalid type: {result.__class_}")
