"""
This module contains :class:`.Conversation`, the base type for all conversations in Royalnet, and
:class:`.DecoratingConversation`, an helper class to instantiate conversations.
"""

from __future__ import annotations
import royalnet.royaltyping as t

import logging
import abc
import royalnet.engineer.teleporter as tp

log = logging.getLogger(__name__)


class Conversation:
    """
    :class:`.Conversation`\\ s are objects which can be called to :attr:`.run` a function which awaits
    :class:`~royalnet.engineer.bullet.projectiles._base.Projectile`\\ s incoming from a
    :class:`~royalnet.engineer.sentry.Sentry` .

    Regular coroutine functions can be used instead of this class, at the cost of slightly worse debug information and
    logging.

    .. seealso:: :class:`.DecoratingConversation`
    """

    @abc.abstractmethod
    async def run(self, **kwargs) -> None:
        """
        Run the conversation.

        :param kwargs: The kwargs passed to the :class:`.Conversation` from the
                       :class:`royalnet.engineer.pda.implementations.base.PDAImplementation` .
                       Usually, they include at least ``_sentry``, but more may be available based on
                       the :class:`royalnet.engineer.pda.implementations.base.PDAImplementation`
                       and available :class:`royalnet.engineer.pda.extensions.base.PDAExtension`\\ s.

        :return: :data:`None` to terminate the conversation, or another :class:`.Conversation` to switch to it.
        """
        raise NotImplementedError()

    def __call__(self, **kwargs) -> t.Awaitable[None]:
        log.debug(f"{self}: Called")
        return self.run(**kwargs)

    def __repr__(self):
        return f"<{self.__class__.__qualname__} #{id(self)}>"


class DecoratingConversation(Conversation):
    """
    A decorator-based approach to creating a :class:`.Conversation`.
    """

    def __init__(self, function: t.ConversationProtocol):
        """
        Either pass a :attr:`.function` to this constructor, or use it as a decorator to create a new
        :class:`.Conversation` .

        >>> @DecoratingConversation
        ... async def decoconv(**kwargs):
        ...     ...
            <DecoratedConversation wrapping <function at 0x...>>
        """

        self.function: t.ConversationProtocol = function
        """
        The function that will be run when the :class:`.Conversation` is called.
        """

    async def run(self, **kwargs) -> None:
        await self.function(**kwargs)

    def __repr__(self):
        return f"<{self.__class__.__qualname__} decorating {self.function}>"


class TeleportingConversation(DecoratingConversation):
    """
    An extension to :class:`.DecoratingConversation` which uses a :class:`~royalnet.engineer.teleporter.Teleporter` to
    type-check and cast the function parameters.
    """

    def __init__(self, function: t.ConversationProtocol):
        super().__init__(tp.Teleporter(function, validate_output=False))

        self.bare_function = function
        """
        The unteleported function.
        """

    def __repr__(self):
        return f"<{self.__class__.__qualname__} teleporting {self.bare_function}>"


__all__ = (
    "Conversation",
    "DecoratingConversation",
    "TeleportingConversation",
)
