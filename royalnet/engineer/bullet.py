"""
Bullets are parts of the data model
"""

from __future__ import annotations
import royalnet.royaltyping as t

import abc
import datetime
import sqlalchemy.orm

from . import exc


class Bullet(metaclass=abc.ABCMeta):
    """
    The abstract base class for Bullet data models.

    **All** methods of :class:`Bullet` can raise :exc:`.exc.BulletException`, such as :class:`.exc.ForbiddenError` or
    :class:`.exc.NotSupportedError`.
    """

    @abc.abstractmethod
    def __hash__(self) -> int:
        """
        :return: A value that uniquely identifies the object in this Python interpreter process.
        """
        raise NotImplementedError()


class Message(Bullet, metaclass=abc.ABCMeta):
    """
    An abstract class representing a chat message.
    """

    async def text(self) -> t.Optional[str]:
        """
        :return: The raw text contents of the message.
        """
        raise exc.NotSupportedError()

    async def timestamp(self) -> t.Optional[datetime.datetime]:
        """
        :return: The :class:`datetime.datetime` at which the message was sent.
        """
        raise exc.NotSupportedError()

    async def reply_to(self) -> t.Optional[Message]:
        """
        :return: The :class:`.Message` this message is a reply to.
        """
        raise exc.NotSupportedError()

    async def channel(self) -> t.Optional[Channel]:
        """
        :return: The :class:`.Channel` this message was sent in.
        """
        raise exc.NotSupportedError()

    async def send_reply(self, text: str) -> t.Optional[Message]:
        """
        Send a reply to this message in the same channel.

        :param text: The text to reply with.
        :return: The sent reply message.
        """
        raise exc.NotSupportedError()


class Channel(Bullet, metaclass=abc.ABCMeta):
    """
    An abstract class representing a channel where messages can be sent.
    """

    async def name(self) -> t.Optional[str]:
        """
        :return: The name of the message channel, such as the chat title.
        """
        raise exc.NotSupportedError()

    async def topic(self) -> t.Optional[str]:
        """
        :return: The topic (description) of the message channel.
        """
        raise exc.NotSupportedError()

    async def users(self) -> t.List[User]:
        """
        :return: A :class:`list` of :class:`.User` who can read messages sent in the channel.
        """
        raise exc.NotSupportedError()

    async def send_message(self, text: str) -> t.Optional[Message]:
        """
        Send a message in this channel.

        :param text: The text to send in the message.
        :return: The sent message.
        """
        raise exc.NotSupportedError()


class User(Bullet, metaclass=abc.ABCMeta):
    """
    An abstract class representing a user who can read or send messages in the chat.
    """

    async def name(self) -> t.Optional[str]:
        """
        :return: The user's name.
        """
        raise exc.NotSupportedError()

    async def database(self, session: sqlalchemy.orm.Session) -> t.Any:
        """
        :param session: A :class:`sqlalchemy.orm.Session` instance to use to fetch the database entry.
        :return: The database entry for this user.
        """
        raise exc.NotSupportedError()

    async def send_message(self, text: str) -> t.Optional[Message]:
        """
        Send a private message to the user.

        :param text: The text to send in the message.
        :return: The sent message.
        """
        raise exc.NotSupportedError()


__all__ = (
    "Bullet",
    "Message",
    "Channel",
    "User",
)
