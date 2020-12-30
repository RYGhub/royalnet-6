"""
Conversations are wrapper classes that can be applied to functions which await
:class:`~royalnet.engineer.bullet.Bullet`\\ s from a :class:`~royalnet.engineer.sentry.Sentry`.
"""

from __future__ import annotations
import royalnet.royaltyping as t

import logging

from . import sentry


log = logging.getLogger(__name__)


class ConversationProtocol(t.Protocol):
    """
    Typing annotation for Conversation functions.
    """
    def __call__(self, *, _sentry: sentry.Sentry, **kwargs) -> t.Awaitable[t.Optional[ConversationProtocol]]:
        ...


class Conversation:
    """
    The base class for Conversations. It does nothing on its own except providing better debug information.
    """

    def __init__(self, f: ConversationProtocol):
        self.f: ConversationProtocol = f

    @classmethod
    def new(cls):
        """
        A decorator that instantiates a new :class:`Conversation` object using the decorated function.

        :return: The created :class:`Conversation` object.
                 It can still be called in the same way as the previous function!
        """
        def decorator(f: ConversationProtocol):
            c = cls(f=f)
            log.debug(f"Created: {repr(c)}")
        return decorator

    def __call__(self, *, _sentry: sentry.Sentry, **kwargs) -> t.Awaitable[t.Optional[ConversationProtocol]]:
        log.debug(f"Calling: {repr(self)}")
        return self.f(_sentry=_sentry, **kwargs)

    def __repr__(self):
        return f"<Conversation #{id(self)}>"


__all__ = (
    "ConversationProtocol",
    "Conversation"
)
