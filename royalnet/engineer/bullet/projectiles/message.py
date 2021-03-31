from __future__ import annotations
from ._imports import *

if t.TYPE_CHECKING:
    from ..contents.message import Message


class MessageReceived(Projectile, metaclass=abc.ABCMeta):
    """
    An abstract class representing the reception of a single message.
    """

    @ap.async_property
    async def message(self) -> "Message":
        """
        :return: The received Message.
        """
        raise exc.NotSupportedError()


class MessageEdited(Projectile, metaclass=abc.ABCMeta):
    """
    An abstract class representing the editing of a single message.
    """

    @ap.async_property
    async def message(self) -> "Message":
        """
        :return: The edited Message.
        """
        raise exc.NotSupportedError()


class MessageDeleted(Projectile, metaclass=abc.ABCMeta):
    """
    An abstract class representing the deletion of a single message.
    """

    @ap.async_property
    async def message(self) -> "Message":
        """
        :return: The edited Message.
        """
        raise exc.NotSupportedError()


__all__ = (
    "MessageReceived",
    "MessageEdited",
    "MessageDeleted",
)
