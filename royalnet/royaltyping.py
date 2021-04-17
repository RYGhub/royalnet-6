"""
This module adds some new common royaltyping to the default typing package.

It should be imported with: ::

    from royalnet.royaltyping import *

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
Kwargs = Mapping[str, Any]
