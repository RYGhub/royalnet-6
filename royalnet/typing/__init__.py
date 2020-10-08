"""This package adds some new common types to the default typing package.

It should be imported with: ::

    from royalnet.typing import *

"""

from typing import *

JSON = Union[
    None,
    int,
    str,
    List["JSON"],
    Dict[str, "JSON"],
]

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
