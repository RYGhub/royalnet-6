"""
.. todo:: Document this.
"""

import royalnet.royaltyping as t
import abc
import contextlib


class PDAExtension(metaclass=abc.ABCMeta):
    """
    .. todo:: Document this.
    """

    def __init__(self):
        pass

    @abc.abstractmethod
    @contextlib.asynccontextmanager
    async def kwargs(self, kwargs: t.Kwargs) -> t.Kwargs:
        """
        .. todo:: Document this.
        """

        yield NotImplemented


__all__ = (
    "PDAExtension",
)
