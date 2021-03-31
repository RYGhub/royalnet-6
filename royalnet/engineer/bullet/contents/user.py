from __future__ import annotations
from ._imports import *

if t.TYPE_CHECKING:
    from .channel import Channel


class User(BulletContents, metaclass=abc.ABCMeta):
    """
    An abstract class representing a user who can read or send messages in the chat.
    """

    @ap.async_property
    async def name(self) -> t.Optional[str]:
        """
        :return: The user's name.
        """
        raise exc.NotSupportedError()

    @ap.async_property
    async def database(self, session: so.Session) -> t.Any:
        """
        :param session: A :class:`sqlalchemy.orm.Session` instance to use to fetch the database entry.
        :return: The database entry for this user.
        """
        raise exc.NotSupportedError()

    async def slide(self) -> "Channel":
        """
        Slide into the DMs of the user and get the private channel they share with with the bot.

        :return: The private channel where you can talk to the user.
        """
        raise exc.NotSupportedError()


__all__ = (
    "User",
)
