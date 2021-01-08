# Module docstring
"""
.. todo:: Document magazines.
"""

# Special imports
from __future__ import annotations
import royalnet.royaltyping as t

# External imports
import logging

# Internal imports
from . import bullet

# Special global objects
log = logging.getLogger(__name__)


# Code
# noinspection PyPep8Naming
class Magazine:
    """
    A reference to all types of bullets to be used when instancing bullets from a bullet.
    """

    _BULLET = bullet.Bullet
    _USER = bullet.User
    _MESSAGE = bullet.Message
    _CHANNEL = bullet.Channel

    @property
    def Bullet(self) -> bullet.Bullet:
        return self._BULLET(mag=self)

    @property
    def User(self) -> bullet.User:
        return self._USER(mag=self)

    @property
    def Message(self) -> bullet.Message:
        return self._MESSAGE(mag=self)

    @property
    def Channel(self) -> bullet.Channel:
        return self._CHANNEL(mag=self)


# Objects exported by this module
__all__ = (
    "Magazine",
)
