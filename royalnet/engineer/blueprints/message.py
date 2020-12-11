from __future__ import annotations
from royalnet.royaltyping import *
import abc
import datetime

from .. import exc
from .blueprint import Blueprint
from .channel import Channel


class Message(Blueprint, metaclass=abc.ABCMeta):
    """
    An abstract class representing a chat message sent in any platform.

    .. seealso:: :class:`.Blueprint`
    """

    def text(self) -> str:
        """
        :return: The raw text contents of the message.
        :raises .exc.NeverAvailableError: If the chat platform does not support text messages.
        :raises .exc.NotAvailableError: If this message does not have any text.
        """
        raise exc.NeverAvailableError()

    def timestamp(self) -> datetime.datetime:
        """
        :return: The :class:`datetime.datetime` at which the message was sent / received.
        :raises .exc.NeverAvailableError: If the chat platform does not support timestamps.
        :raises .exc.NotAvailableError: If this message is special and does not have any timestamp.
        """
        raise exc.NeverAvailableError()

    def reply_to(self) -> Message:
        """
        :return: The :class:`.Message` this message is a reply to.
        :raises .exc.NeverAvailableError: If the chat platform does not support replies.
        :raises .exc.NotAvailableError: If this message is not a reply to any other message.
        """
        raise exc.NeverAvailableError()

    def channel(self) -> Channel:
        """
        :return: The :class:`.Channel` this message was sent in.
        :raises .exc.NeverAvailableError: If the chat platform does not support channels.
        :raises .exc.NotAvailableError: If this message was not sent in any channel.
        """
        raise exc.NeverAvailableError()


__all__ = (
    "Message",
)
