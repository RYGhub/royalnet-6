"""
This module contains the :class:`.FullCommand` and :class:`.PartialCommand` classes, and all
:class:`.CommandException`\\ s.
"""

from __future__ import annotations
import royalnet.royaltyping as t

import logging
import re

from . import conversation as c
from . import sentry as s
from . import bullet as b
from . import teleporter as tp
from . import exc

log = logging.getLogger(__name__)


class CommandException(exc.EngineerException):
    """
    The base :class:`Exception` of the :mod:`royalnet.engineer.command`\\ module.
    """


class CommandNameException(CommandException):
    """
    An :class:`Exception` raised because the :attr:`.FullCommand.names` were invalid.
    """


class MissingNameError(ValueError, CommandNameException):
    """
    :class:`.FullCommand`\\ s must have at least one name, but no names were passed.
    """


class NotAlphanumericNameError(ValueError, CommandNameException):
    """
    All :attr:`.FullCommand.names` should be alphanumeric (a-z 0-9).

    .. seealso:: :meth:`str.isalnum`
    """


class FullCommand(c.Conversation):
    """
    A :class:`.FullCommand` is a :class:`~royalnet.engineer.conversation.Conversation` which is started by a
    :class:`~royalnet.engineer.projectiles.Projectile` having a text matching the :attr:`.pattern`;
    the named capture groups of the pattern are then passed as teleported keyword arguments to :attr:`.f`.

    .. note:: If you're creating a command pack, you shouldn't instantiate directly :class:`.FullCommand` objects, but
              you should use :class:`.PartialCommand`\\ s instead.
    """

    def __init__(self, f: c.ConversationProtocol, *, names: t.List[str], pattern: re.Pattern, lock: bool = True):
        """
        Instantiate a new :class:`.FullCommand`\\ .
        """

        self.plain_f = f
        """
        A reference to the unteleported function :attr:`.f`\\ .
        """

        self.teleported_f = tp.Teleporter(f, validate_input=True, validate_output=False)
        """
        .. todo:: Document this.
        """

        super().__init__(self.run)

        if len(names) < 1:
            raise MissingNameError(f"Passed 'names' list is empty", names)

        self.names: t.List[str] = names
        """
        The names of the command, as a :class:`list` of :class:`str`.
        
        The first element of the list is the primary :attr:`.name`, and will be displayed in help messages.
        """

        self.pattern: re.Pattern = pattern
        """
        The pattern that should be matched by the text of the first 
        :class:`~royalnet.engineer.bullet.projectiles.message.MessageReceived` by the 
        :class:`~royalnet.engineer.conversation.Conversation`\\ .
        """

        self.lock: bool = lock
        """
        If calling this command should :meth:`~royalnet.engineer.dispenser.Dispenser.lock` the calling dispenser.
        
        Locked dispensers cannot run any other :class:`~royalnet.engineer.conversation.Conversation`\\ s but the one 
        which locked it.
        """

    def name(self):
        """
        :return: The primary name of the :class:`.FullCommand`.
        """
        return self.names[0]

    def aliases(self):
        """
        :return: The secondary names of the :class:`.FullCommand`.
        """
        return self.names[1:]

    def __repr__(self):
        plus = f" + {nc-1} other names" if (nc := len(self.names)) > 1 else ""
        return f"<{self.__class__.__qualname__}: {self.name()!r}{plus}>"

    async def run(self, *, _sentry: s.Sentry, **kwargs) -> t.Optional[c.ConversationProtocol]:
        """
        Run the command as if it was a conversation.

        :param _sentry: The :class:`~royalnet.engineer.sentry.Sentry` to use for the conversation.
        :param kwargs: Keyword arguments to pass to the wrapped function :attr:`.f` .
        :return: The result of the wrapped function :attr:`.f` , or :data:`None` if the first projectile received does
                 not satisfy the requirements of the command.
        """

        log.debug(f"Awaiting a bullet...")
        projectile: b.Projectile = await _sentry

        log.debug(f"Received: {projectile!r}")

        log.debug(f"Ensuring the projectile is a MessageReceived: {projectile!r}")
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
                return await super().__call__(
                    _sentry=_sentry,
                    _proj=projectile,
                    _msg=msg,
                    _text=text,
                    **kwargs,
                    **message_kwargs
                )

        else:
            log.debug(f"Passing args to function: {message_kwargs!r}")
            return await super().__call__(
                _sentry=_sentry,
                _proj=projectile,
                _msg=msg,
                _text=text,
                **kwargs,
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
    :class:`.PartialCommand` is a class meant for **building command packs**.

    It provides mostly the same interface as a :class:`.FullCommand`, but some fields are unknown until the command is
    registered in a PDA.

    The missing fields currently are:
    - :attr:`~.FullCommand.name`
    - :attr:`~.FullCommand.pattern`

    At the moment of registration in a PDA, :meth:`.complete` is called, converting it in a :class:`.FullCommand`.
    """

    def __init__(self, f: c.ConversationProtocol, syntax: str, lock: bool = True):
        """
        Instantiate a new :class:`.PartialCommand`\\ .

        .. seealso:: The corresponding decorator form, :meth:`.new`.
        """

        self.f: c.ConversationProtocol = f
        """
        The function to pass to be called when the command is executed.
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
        Decorator factory for creating new :class:`.PartialCommand` with the decorator syntax::

            >>> import royalnet.engineer as engi

            >>> @PartialCommand.new(syntax="")
            ... async def ping(*, _sentry: engi.Sentry, _msg: engi.Message, **__):
            ...     await _msg.reply(text="🏓 Pong!")

            >>> ping
                <PartialCommand <function ping at ...>>

        :return: The decorator to wrap around the :attr:`.f` function.
        """

        def decorator(f: c.ConversationProtocol):
            partial_command = cls(f=f, *args, **kwargs)
            log.debug(f"Created: {partial_command!r}")
            return partial_command

        return decorator

    def complete(self, *, names: t.List[str], pattern: str) -> FullCommand:
        """
        Complete the :class:`.PartialCommand` with the missing fields, creating a :class:`.FullCommand` object.

        :param names: The :attr:`~.FullCommand.names` that the :class:`.FullCommand` should have.
        :param pattern: The pattern to add to the :class:`.PartialCommand`\\ .
                        It is first :meth:`~str.format`\\ ted with the keyword arguments ``name`` and ``syntax``
                        and later :func:`~re.compile`\\ d with the :data:`re.IGNORECASE` flag.

        :return: The completed :class:`.FullCommand`.

        :raises .MissingNameError: If no :attr:`.FullCommand.names` are specified.
        """

        if len(names) < 1:
            raise MissingNameError(f"Passed 'names' list is empty", names)
        for name in names:
            if not name.isalnum():
                raise NotAlphanumericNameError(f"Name is not alphanumeric", name)

        log.debug(f"")
        name_regex = f"(?:{'|'.join(names)})"
        log.debug(f"Completed pattern: {name_regex!r}")

        pattern: re.Pattern = re.compile(pattern.format(name=name_regex, syntax=self.syntax), re.IGNORECASE)
        return FullCommand(f=self.f, names=names, pattern=pattern, lock=self.lock)

    def __repr__(self):
        return f"<{self.__class__.__qualname__} {self.f!r}>"


__all__ = (
    "CommandException",
    "CommandNameException",
    "FullCommand",
    "MissingNameError",
    "NotAlphanumericNameError",
    "PartialCommand",
)
