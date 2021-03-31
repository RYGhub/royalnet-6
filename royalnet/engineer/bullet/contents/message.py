from __future__ import annotations
from ._imports import *

import datetime

if t.TYPE_CHECKING:
    from .channel import Channel
    from .user import User
    from .button_reaction import ButtonReaction


class Message(BulletContents, metaclass=abc.ABCMeta):
    """
    An abstract class representing a chat message.
    """

    @ap.async_property
    async def text(self) -> t.Optional[str]:
        """
        :return: The raw text contents of the message.
        """
        raise exc.NotSupportedError()

    @ap.async_property
    async def timestamp(self) -> t.Optional[datetime.datetime]:
        """
        :return: The :class:`datetime.datetime` at which the message was sent.
        """
        raise exc.NotSupportedError()

    @ap.async_property
    async def reply_to(self) -> t.Optional[Message]:
        """
        :return: The :class:`.Message` this message is a reply to.
        """
        raise exc.NotSupportedError()

    @ap.async_property
    async def channel(self) -> t.Optional["Channel"]:
        """
        :return: The :class:`.Channel` this message was sent in.
        """
        raise exc.NotSupportedError()

    @ap.async_property
    async def sender(self) -> t.Optional["User"]:
        """
        :return: The :class:`.User` who sent this message.
        """
        raise exc.NotSupportedError()

    @ap.async_property
    async def files(self) -> t.Optional[t.List[t.BinaryIO]]:
        """
        :return: A :class:`list` of files attached to the message.
        """
        raise exc.NotSupportedError()

    @ap.async_property
    async def reactions(self) -> t.List["ButtonReaction"]:
        """
        :return: A :class:`list` of reaction buttons attached to the message.
        """

    async def reply(self, *,
                    text: str = None,
                    files: t.List[t.BinaryIO] = None) -> t.Optional[Message]:
        """
        Reply to this message in the same channel it was sent in.

        :param text: The text to reply with.
        :param files: A :class:`list` of files to attach to the message. The file type should be detected automatically
                      by the frontend, and sent in the best format possible (if all files are photos, they should be
                      sent as a photo album, etc.).
        :return: The sent reply message.
        """
        raise exc.NotSupportedError()


__all__ = (
    "Message",
)
