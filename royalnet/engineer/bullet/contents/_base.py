from __future__ import annotations

import abc

from .. import casing


class BulletContents(casing.Casing, metaclass=abc.ABCMeta):
    """
    Abstract base class for bullet contents.
    """


__all__ = (
    "BulletContents",
)
