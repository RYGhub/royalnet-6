"""
This module contains the :class:`.Reaction` projectile.
"""

from __future__ import annotations
from ._imports import *

if t.TYPE_CHECKING:
    from ..contents.user import User
    from ..contents.button_reaction import ButtonReaction


class Reaction(Projectile, metaclass=abc.ABCMeta):
    """
    An abstract class representing a reaction of a single user to a message, generated by clicking on a ButtonReaction.
    """

    @ap.async_property
    async def user(self) -> "User":
        """
        :return: The user who reacted to the message.
        """
        raise exc.NotSupportedError()

    @ap.async_property
    async def button(self) -> "ButtonReaction":
        """
        :return: The ButtonReaction that the user pressed to generate this reaction.
        """
        raise exc.NotSupportedError()


__all__ = (
    "Reaction",
)