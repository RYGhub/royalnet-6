from royalnet.typing import *
import threading
import redis
import queue


__all__ = (
    "Baron",
    "BaronListenerThread",
)


class Baron:
    """The Baron module connects to a Redis database to send and receive messages."""

    def __init__(self,
                 redis_args: Mapping[str, Any],):
        self.publisher: redis.Redis = redis.Redis(**redis_args)
        self.listen_thread: BaronListenerThread = BaronListenerThread(publisher=self.publisher)
        self.was_started = False

    def listener(self) -> redis.client.PubSub:
        return self.listen_thread.listener

    def start(self):
        self.listen_thread.start()
        self.was_started = True


class BaronListenerThread(threading.Thread):
    def __init__(self, publisher: redis.Redis, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.listener: redis.client.PubSub = publisher.pubsub()

    def run(self) -> None:
        self.listener.listen()
