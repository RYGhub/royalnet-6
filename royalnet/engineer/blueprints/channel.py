from __future__ import annotations
from royalnet.royaltyping import *
import abc

from .. import exc
from .blueprint import Blueprint


class Channel(Blueprint, metaclass=abc.ABCMeta):
    """
    An abstract class representing a channel where messages can be sent.

    .. seealso:: :class:`.Blueprint`
    """

    def name(self) -> str:
        """
        :return: The name of the message channel, such as the chat title.
        :raises .exc.NeverAvailableError: If the chat platform does not support channel names.
        :raises .exc.NotAvailableError: If this channel does not have any name.
        """
        raise exc.NeverAvailableError()

    def topic(self) -> str:
        """
        :return: The topic or description of the message channel.
        :raises .exc.NeverAvailableError: If the chat platform does not support channel topics / descriptions.
        :raises .exc.NotAvailableError: If this channel does not have any name.
        """
        raise exc.NeverAvailableError()


__all__ = (
    "Channel",
)
