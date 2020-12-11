from __future__ import annotations
from royalnet.royaltyping import *
import abc
import sqlalchemy.orm

from .. import exc
from .blueprint import Blueprint


class User(Blueprint, metaclass=abc.ABCMeta):
    """
    An abstract class representing a chat user.

    .. seealso:: :class:`.Blueprint`
    """

    def name(self) -> str:
        """
        :return: The user's name.
        :raises .exc.NeverAvailableError: If the chat platform does not support usernames.
        :raises .exc.NotAvailableError: If this user does not have any name.
        """
        raise exc.NeverAvailableError()

    def database(self, session: sqlalchemy.orm.Session) -> Any:
        """
        :param session: A :class:`sqlalchemy.orm.Session` instance to use to fetch the database entry.
        :return: The database entry for this user.
        """


__all__ = (
    "User",
)
