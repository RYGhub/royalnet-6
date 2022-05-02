"""
This module extends :mod:`typing` with some additional types frequently used in :mod:`royalnet`.

It is recommended to import it with the following statement::

    import royalnet.royaltyping as t

"""

from __future__ import annotations

from typing import *
# noinspection PyUnresolvedReferences
from typing import IO, TextIO, BinaryIO
# noinspection PyUnresolvedReferences
from typing import Pattern, Match

JSONScalar = Union[
    None,
    float,
    int,
    str,
]
"""
A non-recursive JSON value: either :data:`None`, a :class:`float`, a :class:`int` or a :class:`str`.
"""

JSON = Union[
    JSONScalar,
    List["JSON"],
    Dict[str, "JSON"],
]
"""
A recursive JSON value: either a :data:`.JSONScalar`, or a :class:`list` of :data:`.JSON` objects, or a :class:`dict` 
of :class:`str` to :data:`.JSON` mappings. 
"""

AsyncFilter = Callable[[Any], Awaitable[Any]]
"""
A function taking an item as input, and returning it in a different form after being awaited.
"""


class ConversationProtocol(Protocol):
    def __call__(self, **kwargs) -> Awaitable[None]:
        ...


Args = Collection[Any]
"""
Any possible combination of positional arguments.
"""

Kwargs = Mapping[str, Any]
"""
Any possible combination of keyword arguments.
"""
