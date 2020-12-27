"""
Commands are used to quickly create single-message conversations
"""

from __future__ import annotations
import royalnet.royaltyping as t

import logging
import functools
import re

from . import bullet
from . import teleporter

log = logging.getLogger(__name__)


class Command:
    """
    A decorator to create a command that can be called from the chat by entering a certain :attr:`.pattern` of
    characters:

    .. code-block:: text

        /echo Hello!
        # Hello!

    """

    def __init__(self,
                 prefix: str,
                 name: str,
                 syntax: str,
                 *,
                 pattern: str = r"^{prefix}{name} {syntax}",
                 doc: str = ""):
        self.prefix: str = prefix
        """
        The prefix used in the command (usually ``/`` or ``!``).
        """

        self.name: str = name
        """
        The name of the command, usually all lowercase.
        """

        self.syntax: str = syntax
        """
        A regex describing the syntax of the command, using named capture groups ``(?P<name>...)`` to capture arguments
        that should be passed to the function.
        """

        self.pattern: re.Pattern = re.compile(pattern.format(prefix=prefix, name=name, syntax=syntax))
        """
        The compiled regex pattern. 
        
        By default, it :meth:`str.format` the passed string with the ``prefix``, ``name`` and ``syntax`` keyword 
        arguments, but this behaviour can be changed by passing a different ``pattern`` to :meth:`__init__`.
        """

        self.doc: str = doc
        """
        A string explaining how this command should be used. Useful for command lists or help commands.
        """

    def __call__(self, f):
        """
        The decorator interface of the command.
        """
        @functools.wraps(f)
        async def decorated(_msg: bullet.Message, **original_kwargs) -> t.Conversation:
            text: str = await _msg.text()
            match: re.Match = self.pattern.search(text)
            match_kwargs: dict = match.groupdict()
            teleported: t.Callable = teleporter.teleporter(is_async=True, validate_output=False)(f)
            return await teleported(_msg=_msg, **original_kwargs, **match_kwargs)
        return decorated
