from __future__ import annotations
from ._imports import *


class Button(BulletContents, metaclass=abc.ABCMeta):
    """
    An abstract class representing a clickable button.
    """

    @ap.async_property
    async def text(self) -> t.Optional[str]:
        """
        :return: The text displayed on the button.
        """
        raise exc.NotSupportedError()


__all__ = (
    "Button",
)
