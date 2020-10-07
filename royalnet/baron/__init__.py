from __future__ import annotations
from royalnet.typing import *
import threading
import redis


__all__ = (
    "Baron",
    "BaronError",
    "BaronAlreadyStartedError",
    "BaronListenerThread",
)


class Baron:
    """The Baron module connects to a Redis database to send and receive messages."""

    def __init__(self,
                 redis_args: Mapping[str, Any],):
        self.publisher: redis.Redis = redis.Redis(**redis_args)
        self.listen_thread: BaronListenerThread = BaronListenerThread(publisher=self.publisher)
        self.is_started = False

    def listener(self) -> redis.client.PubSub:
        """Get the listener of the Baron module."""
        return self.listen_thread.listener

    def start(self) -> Baron:
        """Start the listen thread of the Baron module."""
        if self.is_started:
            raise BaronAlreadyStartedError("This Baron module was already started somewhere else.")
        self.listen_thread.start()
        self.is_started = True
        return self


class BaronError(Exception):
    """An error of the Baron module."""


class BaronAlreadyStartedError(Exception):
    """This Baron module was already started somewhere else."""


class BaronListenerThread(threading.Thread):
    """A Thread that creates a PubSub from a Redis instance and constantly listens to it.

    It ignores all messages that do not have an associated callback."""
    def __init__(self, publisher: redis.Redis, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.listener: redis.client.PubSub = publisher.pubsub()

    def run(self) -> None:
        while True:
            self.listener.listen()
