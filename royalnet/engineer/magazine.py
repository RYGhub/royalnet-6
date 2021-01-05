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
class Magazine:
    """
    A reference to all types of bullets to be used when instancing bullets from a bullet.
    """

    BULLET = bullet.Bullet
    USER = bullet.User
    MESSAGE = bullet.Message
    CHANNEL = bullet.Channel


# Objects exported by this module
__all__ = (
    "Magazine",
)
