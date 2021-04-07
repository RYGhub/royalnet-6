"""
This module contains :class:`.ConversationProtocol`, the typing stub for conversation functions, and
:class:`.Conversation`, a decorator for functions which should help in debugging conversations.
"""

from __future__ import annotations
import royalnet.royaltyping as t

import logging

from . import sentry as s

log = logging.getLogger(__name__)


class ConversationProtocol(t.Protocol):
    """
    Typing stub for :class:`.Conversation`\\ -compatible functions.
    """
    def __call__(self, *, _sentry: s.Sentry, **kwargs) -> t.Awaitable[t.Optional[ConversationProtocol]]:
        ...


class Conversation:
    """
    :class:`.Conversation`\\ s are functions which await
    :class:`~royalnet.engineer.bullet.projectiles._base.Projectile`\\ s incoming from a
    :class:`~royalnet.engineer.sentry.Sentry` .

    This class is callable ( :meth:`.__call__` ), and can be used in place of plain functions to have better debug
    information.
    """

    def __init__(self, f: ConversationProtocol, *_, **__):
        self.f: ConversationProtocol = f
        """
        The function that is wrapped by this class.
         
        It can be called by calling this object as if it was a function::
        
            my_conv(_sentry=_sentry, _msg=msg)
        """

    @classmethod
    def new(cls, *args, **kwargs):
        """
        Decorator factory for creating new :class:`.PartialCommand` with the decorator syntax::

            >>> @Conversation.new()
            ... def my_conv(*, _sentry: s.Sentry, **__):
            ...     pass

            >>> my_conv
                <Conversation #1234>

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
        return self.f(_sentry=_sentry, **kwargs)

    def __repr__(self):
        return f"<{self.__class__.__qualname__} #{id(self)}>"


__all__ = (
    "ConversationProtocol",
    "Conversation"
)
