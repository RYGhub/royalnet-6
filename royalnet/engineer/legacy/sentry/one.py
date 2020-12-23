from __future__ import annotations
from royalnet.royaltyping import *
from .two import Two


class One:
    """
    A class that manages :class:`.Conversation` creation and destruction and dispatches messages to the ones currently
    running.
    """

    def __init__(self):
        self.conversations: List[Two] = []

    async def run(self, cofun: Callable[One, Awaitable[None]], **kwargs) -> None:
        conversation = Two(sentry=self, **kwargs)
        self.conversations.append(conversation)

        state = cofun(conversation=conversation)
        while state:
            state = await state

        self.conversations.remove(conversation)

    def put(self, item):
        for conversation in self.conversations:
            conversation.put(item)

    def __len__(self):
        return len(self.conversations)

    def __repr__(self):
        return f"<Sentry with {len(self.conversations)} active " \
               f"conversation{'s' if len(self.conversations) != 1 else ''}>"


__all__ = (
    "One",
)
