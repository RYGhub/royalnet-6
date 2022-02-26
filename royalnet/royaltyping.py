"""
This module defines adds some common types to the default :mod:`typing` module present in the standard library.

It is recommended to import it with *one* of the following statements::

    import royalnet.royaltyping as t
    from royalnet.royaltyping import *
    from royalnet.royaltyping import <used_objects>

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


WrenchLike = Callable[[Any], Awaitable[Any]]


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
