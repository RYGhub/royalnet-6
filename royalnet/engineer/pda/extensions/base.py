"""
This module contains the base :class:`~royalnet.engineer.pda.extensions.base.PDAExtension`\\ .
"""

import royalnet.royaltyping as t
import abc
import contextlib


class PDAExtension(metaclass=abc.ABCMeta):
    """
    A :class:`.PDAExtension` is an object which extends a
    :class:`~royalnet.engineer.pda.implementations.base.PDAImplementation` by providing additional kwargs to
    :class:`~royalnet.engineer.conversation.Conversation`\\ s.
    """

    @abc.abstractmethod
    @contextlib.asynccontextmanager
    async def kwargs(self, kwargs: t.Kwargs) -> t.Kwargs:
        """
        An :func:`~contextlib.asynccontextmanager` which takes the kwargs that would be passed to the
        :class:`~royalnet.engineer.conversation.Conversation`\\ , modifies them (for example by adding new items) and
        yields them, then performs cleanup operations.
        """

        yield NotImplemented


__all__ = (
    "PDAExtension",
)
