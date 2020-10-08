from __future__ import annotations
from royalnet.typing import *
import logging
import inspect
log = logging.getLogger(__name__)


class Campaign:
    """
        The Campaign module allows for branching generator-based back-and-forths between the software and the
        user.

        A Campaign consists of multiple chained generators.
        """

    def __init__(self, start: Generator[Any, Any, Any]):
        self._current: Generator[Any, Any, Any] = start

    @classmethod
    def create(cls, start: Generator[Any, Any, Any]):
        campaign = cls(start=start)
        result = campaign._current.send(None)
        if result is not None:
            log.warning(f"{campaign._current} returned a non-null value")
        return campaign

    def next(self, data: Any = None):
        result = self._current.send(data)
        if inspect.isgenerator(result):
            self._current.close()
            self._current = result
            result = self._current.send(None)
            if result is not None:
                log.warning(f"{self._current} returned a non-null value")
        return result
