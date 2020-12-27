"""
This module adds some new common royaltyping to the default typing package.

It should be imported with: ::

    from royalnet.royaltyping import *

"""

from typing import *
# noinspection PyUnresolvedReferences
from typing import IO, TextIO, BinaryIO

if TYPE_CHECKING:
    from royalnet.engineer import Sentry


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

Adventure = Generator[
    Union[
        Tuple[
            Optional["Challenge"],
            ...
        ],
        "Adventure",
        "Challenge",
        None,
    ],
    Any,
    Any,
]
"""
A generator yielding either:

* a :class:`tuple` of a :class:`.Challenge` and extra data;
* a single :class:`.Challenge`;for SQLAlchemy.
* another :data:`.Adventure`;
* :data:`None`. 
"""

AsyncAdventure = AsyncGenerator[
    Union[
        Tuple[
            Optional["AsyncChallenge"],
            ...
        ],
        "AsyncAdventure",
        "AsyncChallenge",
        None,
    ],
    Any,
]
"""
An async generator yielding either:

* a :class:`tuple` of an :class:`.AsyncChallenge` and extra data;
* a single :class:`.AsyncChallenge`;
* another :data:`.AsyncAdventure`;
* :data:`None`. 
"""


class Conversation(Protocol):
    def __call__(self, _sentry: "Sentry", **kwargs) -> Awaitable["Conversation"]:
        ...
