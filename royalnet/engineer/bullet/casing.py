"""
This module contains the base :class:`.Casing` class.
"""

from __future__ import annotations

import abc


class Casing(metaclass=abc.ABCMeta):
    """
    :class:`.Casing`\\ s are parts of the data model that :mod:`royalnet.engineer` uses to build a common interface
    between different applications (*PDA implementations*).

    They use :func:`~async_property.async_property` to represent data, as it may be required to fetch it from a remote
    location before it is available.

    **All** their methods can have three different results:

    - :exc:`.exc.CasingException` is raised, meaning that something went wrong during the data retrieval.
      - :exc:`.exc.NotSupportedError` is raised, meaning that the frontend does not support the feature the requested
        data is about (asking for :meth:`~royalnet.engineer.bullet.contents.message.Message.reply_to` in an SMS
        implementation, for example).

    - :data:`None` is returned, meaning that there is no data in that field (if a message is not a reply to anything,
      :meth:`Message.reply_to` will be :data:`None`.

    - The data is returned.
    """

    def __init__(self):
        """
        Instantiate a new instance of this class.
        """

    @abc.abstractmethod
    def __hash__(self) -> int:
        """
        :return: A :class:`int` value that uniquely identifies the object in this Python interpreter process.
        """
        raise NotImplementedError()
