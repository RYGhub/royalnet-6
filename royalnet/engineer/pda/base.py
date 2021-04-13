"""
This module contains the base :class:`.PDA` class.
"""

import asyncio
import royalnet.royaltyping as t
import logging

if t.TYPE_CHECKING:
    from royalnet.engineer.pda.implementations.base import PDAImplementation
    DispenserKey = t.TypeVar("DispenserKey")

log = logging.getLogger(__name__)


class PDA:
    """
    .. todo:: Document this.
    """

    def __init__(self, implementations: list["PDAImplementation"]):
        self.implementations: dict[str, "PDAImplementation"] = {}
        for implementation in implementations:
            implementation.bind(pda=self)
            self.implementations[implementation.name] = implementation

    def __repr__(self):
        return f"<{self.__class__.__qualname__} implementing {', '.join(self.implementations.keys())}>"

    def __len__(self):
        return len(self.implementations)

    async def _run(self):
        log.info("Running all implementations...")
        await asyncio.gather(*[implementation.run() for implementation in self.implementations.values()])
        log.fatal("All implementations have finished running?!")

    def run(self):
        log.debug("Running blockingly all implementations...")
        asyncio.run(self._run())
        log.fatal("Blocking call has finished?!")


__all__ = (
    "PDA",
)
