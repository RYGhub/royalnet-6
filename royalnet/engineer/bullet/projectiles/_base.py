from __future__ import annotations

import abc

from .. import casing


class Projectile(casing.Casing, metaclass=abc.ABCMeta):
    """
    Abstract base class for external events which can be inserted in a dispenser.
    """


__all__ = (
    "Projectile",
)
