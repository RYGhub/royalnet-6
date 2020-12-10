from __future__ import annotations
from royalnet.royaltyping import *
import abc
import datetime
import functools

from . import exc


class Message(metaclass=abc.ABCMeta):
    """
    An abstract class representing a generic chat message sent in any platform.

    To implement it for a specific platform, override :meth:`__hash__` and the methods returning information that the
    platform sometimes provides, either returning the value or raising :exc:`.exc.NotAvailableError`.

    All properties are cached using :func:`functools.lru_cache`, so that if they are successful, they are executed only
    one time.
    """

    @abc.abstractmethod
    def __hash__(self):
        """
        :return: A value that uniquely identifies the message inside this Python process.
        """
        raise NotImplementedError()

    def requires(self, *fields) -> None:
        """
        Ensure that this message has the specified fields, raising the highest priority exception between all the
        fields.

        .. code-block::

            def print_msg(message: Message):
                message.requires(Message.text, Message.timestamp)
                print(f"{message.timestamp().isoformat()}: {message.text()}")

        :raises .exc.NeverAvailableError: If at least one of the fields raised a :exc:`.exc.NeverAvailableError`.
        :raises .exc.NotAvailableError: If no field raised a :exc:`.exc.NeverAvailableError`, but at least one raised a
                                        :exc:`.exc.NotAvailableError`.
        """

        exceptions = []

        for field in fields:
            try:
                field(self)
            except exc.NeverAvailableError as ex:
                exceptions.append(ex)
            except exc.NotAvailableError as ex:
                exceptions.append(ex)

        if len(exceptions) > 0:
            raise max(exceptions, key=lambda e: e.priority)

    @functools.lru_cache()
    def text(self) -> str:
        """
        :return: The raw text contents of the message.
        :raises .exc.NeverAvailableError: If the chat platform does not support text messages.
        :raises .exc.NotAvailableError: If this message does not have any text.
        """
        raise exc.NeverAvailableError()

    @functools.lru_cache()
    def timestamp(self) -> datetime.datetime:
        """
        :return: The :class:`datetime.datetime` at which the message was sent / received.
        :raises .exc.NeverAvailableError: If the chat platform does not support timestamps.
        :raises .exc.NotAvailableError: If this message is special and does not have any timestamp.
        """
        raise exc.NeverAvailableError()

    @functools.lru_cache()
    def reply_to(self) -> Message:
        """
        :return: The :class:`.Message` this message is a reply to.
        :raises .exc.NeverAvailableError: If the chat platform does not support replies.
        :raises .exc.NotAvailableError: If this message is not a reply to any other message.
        """
