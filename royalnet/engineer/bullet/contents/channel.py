from __future__ import annotations
from ._imports import *

if t.TYPE_CHECKING:
    from .message import Message
    from .user import User


class Channel(BulletContents, metaclass=abc.ABCMeta):
    """
    An abstract class representing a channel where messages can be sent.
    """

    @ap.async_property
    async def name(self) -> t.Optional[str]:
        """
        :return: The name of the message channel, such as the chat title.
        """
        raise exc.NotSupportedError()

    @ap.async_property
    async def topic(self) -> t.Optional[str]:
        """
        :return: The topic (description) of the message channel.
        """
        raise exc.NotSupportedError()

    @ap.async_property
    async def users(self) -> t.List["User"]:
        """
        :return: A :class:`list` of :class:`.User` who can read messages sent in the channel.
        """
        raise exc.NotSupportedError()

    async def send_message(self, *,
                           text: str = None,
                           files: t.List[t.BinaryIO] = None) -> t.Optional["Message"]:
        """
        Send a message in the channel.

        :param text: The text to send in the message.
        :param files: A :class:`list` of files to attach to the message. The file type should be detected automatically
                      by the frontend, and sent in the best format possible (if all files are photos, they should be
                      sent as a photo album, etc.).
        :return: The sent message.
        """
        raise exc.NotSupportedError()


__all__ = (
    "Channel",
)
