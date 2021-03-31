# Module docstring
"""

"""

# Special imports
from __future__ import annotations
import royalnet.royaltyping as t

# External imports
import logging
import re

# Internal imports
from . import conversation as c
from . import sentry as s
from . import bullet as b
from . import teleporter as tp

# Special global objects
log = logging.getLogger(__name__)


# Code
class Command(c.Conversation):
    """
    A Command is a :class:`~.conversation.Conversation` which is started by a :class:`~.bullet.Message` having a text
    matching the :attr:`.pattern`; the named capture groups of the pattern are then passed as keyword arguments to
    :attr:`.f`.

    .. info:: Usually you don't directly instantiate commands, you define :class:`.PartialCommand`\\ s in packs which
              are later completed by a runner.
    """

    def __init__(self, f: c.ConversationProtocol, *, names: t.List[str] = None, pattern: re.Pattern, lock: bool = True):
        """
        Create a new :class:`.Command` .
        """
        log.debug(f"Teleporting function: {f!r}")
        teleported = tp.Teleporter(f, validate_input=True, validate_output=False)

        log.debug(f"Initializing Conversation with: {teleported!r}")
        super().__init__(teleported)

        self.names: t.List[str] = names if names else []
        """
        The names of the command, as a :class:`list` of :class:`str`.
        
        The first element of the list is the "main" name, and will be displayed in help messages.
        """

        self.pattern: re.Pattern = pattern
        """
        The pattern that should be matched by the command.
        """

        self.lock: bool = lock
        """
        If calling this command should :meth:`~royalnet.engineer.dispenser.Dispenser.lock` the dispenser.
        """

    def name(self):
        """
        :return: The main name of the Command.
        """
        return self.names[0]

    def aliases(self):
        """
        :return: The aliases (non-main names) of the Command.
        """
        return self.names[1:]

    def __repr__(self):
        if (nc := len(self.names)) > 1:
            plus = f" + {nc-1} other names"
        else:
            plus = ""
        return f"<{self.__class__.__qualname__}: {self.name()!r}{plus}>"

    async def run(self, *, _sentry: s.Sentry, **base_kwargs) -> t.Optional[c.ConversationProtocol]:
        log.debug(f"Awaiting a bullet...")
        projectile: b.Projectile = await _sentry

        log.debug(f"Received: {projectile!r}")

        log.debug(f"Ensuring a message was received: {projectile!r}")
        if not isinstance(projectile, b.MessageReceived):
            log.debug(f"Returning: {projectile!r} is not a message")
            return

        log.debug(f"Getting message of: {projectile!r}")
        if not (msg := await projectile.message):
            log.warning(f"Returning: {projectile!r} has no message")
            return

        log.debug(f"Getting message text of: {msg!r}")
        if not (text := await msg.text):
            log.debug(f"Returning: {msg!r} has no text")
            return

        log.debug(f"Searching for pattern: {text!r}")
        if not (match := self.pattern.search(text)):
            log.debug(f"Returning: Couldn't find pattern in {text!r}")
            return

        log.debug(f"Match successful, getting capture groups of: {match!r}")
        message_kwargs: t.Dict[str, str] = match.groupdict()

        if self.lock:
            log.debug(f"Locking the dispenser...")

            with _sentry.dispenser().lock(self):
                log.debug(f"Passing args to function: {message_kwargs!r}")
                return await super().run(
                    _sentry=_sentry,
                    _proj=projectile,
                    _msg=msg,
                    _text=text,
                    **base_kwargs,
                    **message_kwargs
                )

        else:
            log.debug(f"Passing args to function: {message_kwargs!r}")
            return await super().run(
                _sentry=_sentry,
                _proj=projectile,
                _msg=msg,
                _text=text,
                **base_kwargs,
                **message_kwargs
            )

    def help(self) -> t.Optional[str]:
        """
        Get help about this command. This defaults to returning the docstring of :attr:`.f` .

        :return: The help :class:`str` for this command, or :data:`None` if the command has no docstring.
        """
        return self.f.__doc__


class PartialCommand:
    """
    A PartialCommand is a :class:`.Command` having an unknown :attr:`~.Command.name` and :attr:`~.Command.pattern` at
    the moment of creation.

    They can specified later using :meth:`.complete`.
    """
    def __init__(self, f: c.ConversationProtocol, syntax: str, lock: bool = True):
        """
        Create a new :class:`.PartialCommand` .

        .. seealso:: :meth:`.new`
        """

        self.f: c.ConversationProtocol = f
        """
        The function to pass to :attr:`.c.Conversation.f`.
        """

        self.syntax: str = syntax
        """
        Part of the pattern from where the arguments should be captured.
        """

        self.lock: bool = lock
        """
        If calling this command should :meth:`~royalnet.engineer.dispenser.Dispenser.lock` the dispenser.
        """

    @classmethod
    def new(cls, *args, **kwargs):
        """
        A decorator that instantiates a new :class:`Conversation` object using the decorated function.

        :return: The created :class:`Conversation` object.
                 It can still be called in the same way as the previous function!
        """
        def decorator(f: c.ConversationProtocol):
            partial_command = cls(f=f, *args, **kwargs)
            log.debug(f"Created: {partial_command!r}")
            return partial_command

        return decorator

    def complete(self, *, names: t.List[str] = None, pattern: str) -> Command:
        """
        Complete the :class:`.PartialCommand` with names and a pattern, creating a :class:`Command` object.

        :param names: The names of the command. See :attr:`.Command.names` .
        :param pattern: The pattern to add to the PartialCommand. It is first :meth:`~str.format`\\ ted with the keyword
                        arguments ``name`` and ``syntax`` and later :func:`~re.compile`\\ d with the
                        :data:`re.IGNORECASE` flag.
        :return: The complete :class:`Command`.
        """
        if names is None:
            names = []
        if len(names) < 1:
            raise ValueError("Commands must have at least one name.")
        for name in names:
            if not name.isalnum():
                raise ValueError(f"Name is not alphanumeric: {name!r}")

        name_regex = f"(?:{'|'.join(names)})"
        log.debug(f"Completed pattern: {name_regex!r}")

        pattern: re.Pattern = re.compile(pattern.format(name=name_regex, syntax=self.syntax), re.IGNORECASE)
        return Command(f=self.f, names=names, pattern=pattern, lock=self.lock)

    def __repr__(self):
        return f"<{self.__class__.__qualname__} {self.f!r}>"


# Objects exported by this module
__all__ = (
    "Command",
    "PartialCommand",
)
