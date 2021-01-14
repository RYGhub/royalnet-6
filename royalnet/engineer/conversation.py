# Module docstring
"""
Conversations are wrapper classes that can be applied to functions which await
:class:`~royalnet.engineer.bullet.Bullet`\\ s from a :class:`~royalnet.engineer.sentry.Sentry`.
"""

# Special imports
from __future__ import annotations
import royalnet.royaltyping as t

# External imports
import logging

# Internal imports
from . import sentry as s


# Special global objects
log = logging.getLogger(__name__)


# Code
class ConversationProtocol(t.Protocol):
    """
    Typing annotation for Conversation functions.
    """
    def __call__(self, *, _sentry: s.Sentry, **kwargs) -> t.Awaitable[t.Optional[ConversationProtocol]]:
        ...


class Conversation:
    """
    The base class for Conversations. It does nothing on its own except providing better debug information.
    """

    def __init__(self, f: ConversationProtocol, *_, **__):
        self.f: ConversationProtocol = f
        """
        The function that was wrapped by this conversation.
         
        It can be called by calling this object as it was a function::
        
            my_conv(_sentry=_sentry, _msg=msg)
        """

    @classmethod
    def new(cls, *args, **kwargs):
        """
        A decorator that instantiates a new :class:`Conversation` object using the decorated function.

        :return: The created :class:`Conversation` object.
                 It can still be called in the same way as the previous function!
        """
        def decorator(f: ConversationProtocol):
            c = cls(f=f, *args, **kwargs)
            log.debug(f"Created: {c!r}")
            return c
        return decorator

    def __call__(self, *, _sentry: s.Sentry, **kwargs) -> t.Awaitable[t.Optional[ConversationProtocol]]:
        log.debug(f"Calling: {self!r}")
        return self.run(_sentry=_sentry, **kwargs)

    async def run(self, *, _sentry: s.Sentry, **kwargs) -> t.Optional[ConversationProtocol]:
        """
        The coroutine function that generates the coroutines returned by :meth:`.__call__` .

        It is a :class:`Conversation` itself.
        """
        log.debug(f"Running: {self!r}")
        return await self.f(_sentry=_sentry, **kwargs)

    def __repr__(self):
        return f"<{self.__class__.__qualname__} #{id(self)}>"


__all__ = (
    "ConversationProtocol",
    "Conversation"
)
