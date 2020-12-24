"""

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
        :raises .exc.NotSupportedError: If the frontend does not support text messages.
        """
        raise exc.NotSupportedError()

    async def timestamp(self) -> t.Optional[datetime.datetime]:
        """
        :return: The :class:`datetime.datetime` at which the message was sent.
        :raises .exc.NotSupportedError: If the frontend does not support timestamps.
        """
        raise exc.NotSupportedError()

    async def reply_to(self) -> t.Optional[Message]:
        """
        :return: The :class:`.Message` this message is a reply to.
        :raises .exc.NotSupportedError: If the frontend does not support replies.
        """
        raise exc.NotSupportedError()

    async def channel(self) -> t.Optional[Channel]:
        """
        :return: The :class:`.Channel` this message was sent in.
        :raises .exc.NotSupportedError: If the frontend does not support channels.
        """
        raise exc.NotSupportedError()


class Channel(Bullet, metaclass=abc.ABCMeta):
    """
    An abstract class representing a channel where messages can be sent.
    """

    async def name(self) -> t.Optional[str]:
        """
        :return: The name of the message channel, such as the chat title.
        :raises .exc.NotSupportedError: If the frontend does not support channel names.
        """
        raise exc.NotSupportedError()

    async def topic(self) -> t.Optional[str]:
        """
        :return: The topic (description) of the message channel.
        :raises .exc.NotSupportedError: If the frontend does not support channel topics / descriptions.
        """
        raise exc.NotSupportedError()

    async def users(self) -> t.List[User]:
        """
        :return: A :class:`list` of :class:`.User` who can read messages sent in the channel.
        :raises .exc.NotSupportedError: If the frontend does not support such a feature.
        """
        raise exc.NotSupportedError()


class User(Bullet, metaclass=abc.ABCMeta):
    """
    An abstract class representing a user who can read or send messages in the chat.
    """

    async def name(self) -> t.Optional[str]:
        """
        :return: The user's name.
        :raises .exc.NotSupportedError: If the frontend does not support usernames.
        """
        raise exc.NotSupportedError()

    async def database(self, session: sqlalchemy.orm.Session) -> t.Any:
        """
        :param session: A :class:`sqlalchemy.orm.Session` instance to use to fetch the database entry.
        :return: The database entry for this user.
        """
        raise exc.NotSupportedError()


__all__ = (
    "Bullet",
    "Message",
    "Channel",
    "User",
)
