"""
Bullets are parts of the data model that :mod:`royalnet.engineer` uses to build a common interface between different
chat apps (*frontends*).

They exclusively use coroutine functions to access data, as it may be required to fetch it from a remote location before
it is available.

**All** coroutine functions can have three different results:

- :exc:`.exc.BulletException` is raised, meaning that something went wrong during the data retrieval.
  - :exc:`.exc.NotSupportedError` is raised, meaning that the frontend does not support the feature the requested data
    is about (asking for :meth:`.Message.reply_to` in an IRC frontend, for example).
- :data:`None` is returned, meaning that there is no data in that field (if a message is not a reply to anything,
  :meth:`Message.reply_to` will be :data:`None`.
- The data is returned.

To instantiate a new :class:`Bullet` from a bullet, you should use the methods of :attr:`.Bullet.mag`.
"""

from __future__ import annotations
import royalnet.royaltyping as t

import abc
import datetime
import sqlalchemy.orm
import async_property as ap

from . import exc

if t.TYPE_CHECKING:
    from . import magazine


class Bullet(metaclass=abc.ABCMeta):
    """
    The abstract base class for :mod:`~royalnet.engineer.bullet` models.
    """

    def __init__(self, mag: "magazine.Magazine"):
        """
        Instantiate a new :class:`.Bullet` .
        """

        self.mag: "magazine.Magazine" = mag
        """
        The :class:`.magazine.Magazine` to use when instantiating new :class:`.Bullet`\\ s.
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

    @ap.async_cached_property
    async def text(self) -> t.Optional[str]:
        """
        :return: The raw text contents of the message.
        """
        raise exc.NotSupportedError()

    @ap.async_cached_property
    async def timestamp(self) -> t.Optional[datetime.datetime]:
        """
        :return: The :class:`datetime.datetime` at which the message was sent.
        """
        raise exc.NotSupportedError()

    @ap.async_cached_property
    async def reply_to(self) -> t.Optional[Message]:
        """
        :return: The :class:`.Message` this message is a reply to.
        """
        raise exc.NotSupportedError()

    @ap.async_cached_property
    async def channel(self) -> t.Optional[Channel]:
        """
        :return: The :class:`.Channel` this message was sent in.
        """
        raise exc.NotSupportedError()

    @ap.async_cached_property
    async def files(self) -> t.Optional[t.List[t.BinaryIO]]:
        """
        :return: A :class:`list` of files attached to the message.
        """
        raise exc.NotSupportedError()

    @ap.async_cached_property
    async def reactions(self) -> t.List[ReactionButton]:
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


class Channel(Bullet, metaclass=abc.ABCMeta):
    """
    An abstract class representing a channel where messages can be sent.
    """

    @ap.async_cached_property
    async def name(self) -> t.Optional[str]:
        """
        :return: The name of the message channel, such as the chat title.
        """
        raise exc.NotSupportedError()

    @ap.async_cached_property
    async def topic(self) -> t.Optional[str]:
        """
        :return: The topic (description) of the message channel.
        """
        raise exc.NotSupportedError()

    @ap.async_cached_property
    async def users(self) -> t.List[User]:
        """
        :return: A :class:`list` of :class:`.User` who can read messages sent in the channel.
        """
        raise exc.NotSupportedError()

    async def send_message(self, *,
                           text: str = None,
                           files: t.List[t.BinaryIO] = None) -> t.Optional[Message]:
        """
        Send a message in the channel.

        :param text: The text to send in the message.
        :param files: A :class:`list` of files to attach to the message. The file type should be detected automatically
                      by the frontend, and sent in the best format possible (if all files are photos, they should be
                      sent as a photo album, etc.).
        :return: The sent message.
        """
        raise exc.NotSupportedError()


class User(Bullet, metaclass=abc.ABCMeta):
    """
    An abstract class representing a user who can read or send messages in the chat.
    """

    @ap.async_cached_property
    async def name(self) -> t.Optional[str]:
        """
        :return: The user's name.
        """
        raise exc.NotSupportedError()

    @ap.async_cached_property
    async def database(self, session: sqlalchemy.orm.Session) -> t.Any:
        """
        :param session: A :class:`sqlalchemy.orm.Session` instance to use to fetch the database entry.
        :return: The database entry for this user.
        """
        raise exc.NotSupportedError()

    async def slide(self) -> Channel:
        """
        Slide into the DMs of the user and get the private channel they share with with the bot.

        :return: The private channel where you can talk to the user.
        """
        raise exc.NotSupportedError()


class Button(Bullet, metaclass=abc.ABCMeta):
    """
    An abstract class representing a clickable button.
    """

    @ap.async_cached_property
    async def text(self) -> t.Optional[str]:
        """
        :return: The text displayed on the button.
        """
        raise exc.NotSupportedError()


class ReactionButton(Button, metaclass=abc.ABCMeta):
    """
    An abstract class representing a clickable reaction to a message.
    """

    @ap.async_property
    async def reactions(self) -> t.List[Reaction]:
        """
        :return: The list of reactions generated by this button. It may vary every time this property is accessed,
                 based on the users who have reacted to the button at the time of access.
        """
        raise exc.NotSupportedError()

    @ap.async_property
    async def count(self) -> int:
        """
        :return: The count of reactions that this button generated. It may vary every time this property is accessed,
                 based on how many users have reacted to the button at the time of access.
        """
        raise exc.NotSupportedError()

    @ap.async_cached_property
    async def message(self) -> t.Optional[Message]:
        """
        :return: The message this button is attached to. Can be :data:`None`, if the button hasn't been attached to a
                 message yet.
        """
        raise exc.NotSupportedError()


class Reaction(Bullet, metaclass=abc.ABCMeta):
    """
    An abstract class representing a reaction of a single user to a message, generated by clicking on a ReactionButton.
    """

    @ap.async_cached_property
    async def user(self) -> User:
        """
        :return: The user who reacted to the message.
        """
        raise exc.NotSupportedError()

    @ap.async_cached_property
    async def button(self) -> ReactionButton:
        """
        :return: The ReactionButton that the user pressed to generate this reaction.
        """
        raise exc.NotSupportedError()


__all__ = (
    "Bullet",
    "Message",
    "Channel",
    "User",
    "Button",
    "ReactionButton",
    "Reaction",
)
