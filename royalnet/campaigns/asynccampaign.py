from __future__ import annotations
from royalnet.typing import *
import logging
import inspect
log = logging.getLogger(__name__)


class AsyncCampaign:
    """
    The AsyncCampaign module allows for branching asyncgenerator-based back-and-forths between the software and the
    user.

    An AsyncCampaign consists of multiple chained asyncgenerators.
    """
    def __init__(self, start: AsyncGenerator[Any, Any]):
        self._current: AsyncGenerator[Any, Any] = start

    @classmethod
    async def create(cls, start: AsyncGenerator[Any, Any]):
        if not inspect.isasyncgen(start):
            raise TypeError(f"expected async_generator for 'start', received {start.__class__.__qualname__}")
        campaign = cls(start=start)
        result = await campaign._current.asend(None)
        if result is not None:
            log.warning(f"{campaign._current} returned a non-null value")
        return campaign

    async def _asend(self, data: Any) -> Any:
        try:
            return await self._current.asend(data)
        except RuntimeError:
            log.error(f"{self._current} is being used unexpectedly by something else!")
            raise

    async def _athrow(self, typ: Type[BaseException], val: Optional[BaseException], tb: Any) -> Any:
        try:
            return await self._current.athrow(typ, val, tb)
        except RuntimeError:
            log.error(f"{self._current} is being used unexpectedly by something else!")
            raise

    async def _aclose(self) -> None:
        try:
            await self._current.aclose()
        except RuntimeError:
            log.error(f"{self._current} is being used unexpectedly by something else!")
            raise

    async def next(self, data: Any = None):
        result = await self._asend(data)
        if inspect.isasyncgen(result):
            await self._aclose()
            self._current = result
            result = await self._asend(None)
            if result is not None:
                log.warning(f"{self._current} returned a non-null value")
        return result
