# Module docstring
"""
Magazines are references to the bullet classes used by a specific frontend; they allow bullets to instance each other
without tying the instantiations to specific classes.
"""

# Special imports
from __future__ import annotations
import royalnet.royaltyping as t

# External imports
import functools
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
    def Bullet(self) -> functools.partial[bullet.Bullet]:
        log.debug(f"Extracting Bullet from Magazine: {self._BULLET!r}")
        return functools.partial(self._BULLET, mag=self)

    @property
    def User(self) -> functools.partial[bullet.User]:
        log.debug(f"Extracting User from Magazine: {self._USER!r}")
        return functools.partial(self._USER, mag=self)

    @property
    def Message(self) -> functools.partial[bullet.Message]:
        log.debug(f"Extracting Message from Magazine: {self._MESSAGE!r}")
        return functools.partial(self._MESSAGE, mag=self)

    @property
    def Channel(self) -> functools.partial[bullet.Channel]:
        log.debug(f"Extracting Channel from Magazine: {self._CHANNEL!r}")
        return functools.partial(self._CHANNEL, mag=self)


# Objects exported by this module
__all__ = (
    "Magazine",
)
