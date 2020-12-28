"""
Commands are used to quickly create single-message conversations
"""

from __future__ import annotations
import royalnet.royaltyping as t

import logging
import re

from . import teleporter
from . import bullet

log = logging.getLogger(__name__)


class Command:
    """
    A class that allows creating commands which can be called from the chat by entering a certain :attr:`.pattern` of
    characters:

    .. code-block:: text

        /echo Hello!
        # Hello!

    .. todo:: Improve the docstring of :class:`.Command`.
    """

    def __init__(self,
                 prefix: str,
                 name: str,
                 syntax: str,
                 conversation: t.Conversation,
                 *,
                 pattern: str = r"^{prefix}{name} ?{syntax}",
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

        self.conversation: t.Conversation = conversation
        """
        The conversation to run when this command is called.
        """

    @classmethod
    def new(cls,
            prefix: str,
            name: str,
            syntax: str,
            *,
            pattern: str = r"^{prefix}{name} {syntax}",
            doc: str = ""):
        """
        Create a new :class:`.Command` using the decorated function as :attr:`.conversation`.
        :return: The created :class:`.Command`.
        """
        def decorator(f):
            log.debug(f"Making function {f} a teleporter...")
            teleporter_f = teleporter.teleport(is_async=True, validate_output=False)(f)

            log.debug(f"Creating command: {prefix} {name} {syntax} - {doc}")
            return cls(prefix=prefix, name=name, syntax=syntax, conversation=teleporter_f, pattern=pattern, doc=doc)
        return decorator

    async def run(self, _msg: bullet.Message, **original_kwargs) -> t.Optional[t.Conversation]:
        """
        Run the command.

        :param _msg: The the message that was received.
        """
        log.debug(f"Getting text of {_msg}...")
        text = await _msg.text()

        log.debug(f"Matching text {text} to {self.pattern}...")
        match: re.Match = self.pattern.search(text)
        if match is None:
            log.debug(f"Pattern didn't match, returning...")
            return

        log.debug(f"Pattern matched, getting named groups...")
        match_kwargs: t.Dict[str, str] = match.groupdict()

        log.debug(f"Running teleported function with args: {match_kwargs}")
        return await self.conversation(_msg=_msg, **original_kwargs, **match_kwargs)


__all__ = (
    "Command",
)
