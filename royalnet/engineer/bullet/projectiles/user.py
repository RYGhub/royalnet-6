"""
This module contains the projectiles related to user actions, such as :class:`.UserJoined`, :class:`.UserLeft` and
:class:`.UserUpdate`.
"""

from __future__ import annotations
from ._imports import *

if t.TYPE_CHECKING:
    from ..contents.user import User


class UserJoined(Projectile, metaclass=abc.ABCMeta):
    """
    An abstract class representing an user who just joined the chat channel.
    """

    @ap.async_property
    async def user(self) -> "User":
        """
        :return: The user who joined.
        """
        raise exc.NotSupportedError()


class UserLeft(Projectile, metaclass=abc.ABCMeta):
    """
    An abstract class representing an user who just left the chat channel.
    """

    @ap.async_property
    async def user(self) -> "User":
        """
        :return: The user who left.
        """
        raise exc.NotSupportedError()


class UserUpdate(Projectile, metaclass=abc.ABCMeta):
    """
    An abstract class representing a change in status of an user in the chat channel.
    """

    @ap.async_property
    async def user(self) -> "User":
        """
        :return: The user who joined.
        """
        raise exc.NotSupportedError()


__all__ = (
    "UserJoined",
    "UserLeft",
    "UserUpdate",
)
