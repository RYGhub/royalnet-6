"""

"""

from __future__ import annotations
import royalnet.royaltyping as t

import abc

from . import exc


class Event(metaclass=abc.ABCMeta):
    """
    The abstract base class for events transiting through the pipeline.
    """
