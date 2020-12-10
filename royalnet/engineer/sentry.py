from royalnet.royaltyping import *
import logging
import asyncio

log = logging.getLogger(__name__)


class Sentry:
    """
    A class that allows using the ``await`` keyword to suspend a command execution until a new message is received.
    """

    def __init__(self):
        self.queue = asyncio.queues.Queue()

    def __repr__(self):
        return f"<Sentry, {self.queue.qsize()} items queued>"

    async def wait_for_item(self) -> Any:
        log.debug("Waiting for an item...")
        return await self.queue.get()
