"""
.. todo:: Document this.
"""

import royalnet.royaltyping as t
import abc
import contextlib
import asyncio
import logging
from royalnet.engineer.dispenser import Dispenser, LockedDispenserError

if t.TYPE_CHECKING:
    from royalnet.engineer.conversation import ConversationProtocol
    from royalnet.engineer.pda.extensions.base import PDAExtension
    from royalnet.engineer.pda.base import PDA
    from royalnet.engineer.command import PartialCommand, FullCommand
    from royalnet.engineer.bullet.projectiles import Projectile

DispenserKey = t.TypeVar("DispenserKey")


class PDAImplementation(metaclass=abc.ABCMeta):
    """
    .. todo:: Document this.
    """

    def __init__(self, name: str, extensions: list["PDAExtension"] = None):
        self.name: str = f"{self.namespace}.{name}"
        """
        .. todo:: Document this.
        """

        self.extensions: list["PDAExtension"] = extensions or []
        """
        .. todo:: Document this.
        """

        self.bound_to: t.Optional["PDA"] = None
        """
        .. todo:: Document this.
        """

        self.logger_name: str = f"{__name__}.PDAImplementation.{self.namespace}.{name}"
        """
        .. todo:: Document this.
        """

        self.log: logging.Logger = logging.getLogger(self.logger_name)
        """
        .. todo:: Document this.
        """

    def __repr__(self):
        return f"<PDAImplementation {self.name}>"

    def __str__(self):
        return self.name

    def bind(self, pda: "PDA") -> None:
        """
        .. todo:: Document this.
        """

        self.log.debug(f"Trying to bind to {pda!r}...")
        if self.bound_to is not None:
            self.log.error(f"Already bound to {pda!r}!")
            raise ImplementationAlreadyBoundError()

        self.bound_to = pda
        self.log.info(f"Bound to {pda!r}!")

    @property
    @abc.abstractmethod
    def namespace(self):
        """
        .. todo:: Document this.
        """

        raise NotImplementedError()

    @abc.abstractmethod
    async def run(self):
        """
        .. todo:: Document this.
        """

        raise NotImplementedError()


class ImplementationException(Exception):
    """
    .. todo:: Document this.
    """


class ImplementationAlreadyBoundError(ImplementationException):
    """
    .. todo:: Document this.
    """


class ConversationListImplementation(PDAImplementation, metaclass=abc.ABCMeta):
    """
    A :class:`.PDAImplementation` which instantiates multiple :class:`~royalnet.engineer.conversation.Conversation`\\ s
    before putting a :class:`~royalnet.engineer.bullet.projectile.Projectile` in a
    :class:`~royalnet.engineer.dispenser.Dispenser` .
    """

    def __init__(self, name: str, extensions: list["PDAExtension"] = None):
        super().__init__(name=name, extensions=extensions)

        self.conversations: list["ConversationProtocol"] = self._create_conversations()
        """
        .. todo:: Document this.
        """

        self.dispensers: dict[DispenserKey, "Dispenser"] = self._create_dispensers()
        """
        .. todo:: Document this.
        """

    def _create_conversations(self) -> list["ConversationProtocol"]:
        """
        Create the :attr:`.conversations` :class:`list` of the :class:`.ConversationListPDA`\\ .

        :return: The created :class:`list`\\ .
        """

        self.log.debug(f"Creating conversations list...")
        return []

    def _create_dispensers(self) -> dict[t.Any, "Dispenser"]:
        """
        Create the :attr:`.dispensers` dictionary of the PDA.

        :return: The created dictionary (empty by default).
        """

        self.log.debug(f"Creating dispensers list...")
        return {}

    def get_dispenser(self, key: "DispenserKey") -> t.Optional["Dispenser"]:
        """
        Get a :class:`~royalnet.engineer.dispenser.Dispenser` from :attr:`.dispenser` knowing its key.

        :param key: The key to get the dispenser with.
        :return: The retrieved dispenser.

        .. seealso:: :meth:`dict.get`
        """

        self.log.debug(f"Getting dispenser: {key!r}")
        return self.dispensers.get(key)

    def _create_dispenser(self) -> "Dispenser":
        """
        Create a new :class:`~royalnet.engineer.dispenser.Dispenser` .

        :return: The created :class:`~royalnet.engineer.dispenser.Dispenser` .
        """

        self.log.debug(f"Creating new dispenser...")
        return Dispenser()

    def get_or_create_dispenser(self, key: "DispenserKey") -> "Dispenser":
        """
        Try to :meth:`.get_dispenser` the :class:`~royalnet.engineer.dispenser.Dispenser` with the specified key, or
        :meth:`._create_dispenser` a new one if it isn't available.

        :param key: The key of the :class:`~royalnet.engineer.dispenser.Dispenser` .
        :return: The retrieved or created :class:`~royalnet.engineer.dispenser.Dispenser` .
        """

        if key not in self.dispensers:
            self.log.debug(f"{self!r}: Dispenser {key!r} does not exist, creating a new one...")
            self.dispensers[key] = self._create_dispenser()
        return self.get_dispenser(key=key)

    @contextlib.asynccontextmanager
    async def kwargs(self, conv: "ConversationProtocol") -> t.Kwargs:
        """
        :func:`contextlib.asynccontextmanager` factory which yields the arguments to pass to newly created
        :class:`~royalnet.engineer.conversation.Conversation`\\ s .

        By default, the following arguments are passed:
        - ``_pda``: contains the :class:`.PDA` this implementation is bound to.
        - ``_imp``: contains this :class:`.PDAImplementation` .
        - ``_conv``: contains the :class:`~royalnet.engineer.conversation.Conversation` which was just created.

        :param conv: The :class:`~royalnet.engineer.conversation.Conversation` to create the args for.
        :return: The corresponding :func:`contextlib.asynccontextmanager`\\ .
        """
    
        self.log.debug(f"Creating kwargs for: {conv!r}")

        default_kwargs = {
            "_pda": self.bound_to,
            "_imp": self,
            "_conv": conv,
        }

        async with self._kwargs(default_kwargs, self.extensions) as kwargs:
            self.log.info(f"Yielding kwargs for {conv!r}: {kwargs!r}")
            yield kwargs

    @contextlib.asynccontextmanager
    async def _kwargs(self, kwargs: t.Kwargs, remaining: list["PDAExtension"]) -> t.Kwargs:
        """
        :func:`contextlib.asynccontextmanager` factory used internally to recurse the generation and cleanup of
        :meth:`kwargs` .

        :param kwargs: The current ``kwargs`` .
        :param remaining: The extensions that haven't been processed yet.
        :return: The corresponding :func:`contextlib.asynccontextmanager`\\ .
        """

        if len(remaining) == 0:
            self.log.debug(f"Kwargs recursion ended!")
            yield kwargs
        else:
            extension = remaining[0]
            self.log.debug(f"Getting kwargs from {extension}, {len(remaining)} left...")
            async with extension.kwargs(kwargs) as kwargs:
                self.log.debug(f"Recursing...")
                async with self._kwargs(kwargs=kwargs, remaining=remaining[1:]) as kwargs:
                    self.log.debug(f"Bubbling up yields...")
                    yield kwargs

    def register_conversation(self, conversation: "ConversationProtocol") -> None:
        """
        Register a new :class:`~royalnet.engineer.conversation.Conversation` to be run when a new
        :class:`~royalnet.engineer.bullet.projectile.Projectile` is :meth:`.put`\\ .

        :param conversation: The :class:`~royalnet.engineer.conversation.Conversation` to register.
        """

        self.log.debug(f"Registering: {conversation!r}")
        self.conversations.append(conversation)

    def unregister_conversation(self, conversation: "ConversationProtocol") -> None:
        """
        Unregister a :class:`~royalnet.engineer.conversation.Conversation`, stopping it from being run when a new
        :class:`~royalnet.engineer.bullet.projectile.Projectile` is :meth:`.put`\\ .

        :param conversation: The :class:`~royalnet.engineer.conversation.Conversation` to unregister.
        """

        self.log.debug(f"Unregistering: {conversation!r}")
        self.conversations.remove(conversation)

    @abc.abstractmethod
    def _partialcommand_pattern(self, partial: "PartialCommand") -> str:
        """
        The pattern to use when :meth:`.complete_partialcommand` is called.

        :param partial: The :class:`~royalnet.engineer.command.PartialCommand` to complete.
        :return: A :class:`str` to use as pattern.
        """

        raise NotImplementedError()

    def complete_partialcommand(self, partial: "PartialCommand", names: list[str]) -> "FullCommand":
        """
        Complete a :class:`~royalnet.engineer.command.PartialCommand` with its missing fields.

        :param partial: The :class:`~royalnet.engineer.command.PartialCommand` to complete.
        :param names: The :attr:`~royalnet.engineer.command.FullCommand.names` of that the command should have.
        :return: The completed :class:`~royalnet.engineer.command.FulLCommand` .
        """

        self.log.debug(f"Completing: {names!r} → {partial!r}")
        return partial.complete(names=names, pattern=self._partialcommand_pattern(partial))

    def register_partialcommand(self, partial: "PartialCommand", names: list[str]) -> "FullCommand":
        """
        A combination of :meth:`.register_conversation` and :meth:`.complete_partialcommand` .

        :param partial: The :class:`~royalnet.engineer.command.PartialCommand` to complete.
        :param names: The :attr:`~royalnet.engineer.command.FullCommand.names` of that the command should have.
        :return: The completed :class:`~royalnet.engineer.command.FulLCommand` .
        """

        full = self.complete_partialcommand(partial=partial, names=names)
        self.register_conversation(full)
        return full

    async def _run_conversation(self, dispenser: "Dispenser", conv: "ConversationProtocol") -> None:
        """
        Run the passed :class:`~royalnet.engineer.conversation.Conversation` in the passed
        :class:`~royalnet.engineer.dispenser.Dispenser`\\ , while passing the :meth:`.kwargs` provided by the
        :class:`.PDA` .

        :param dispenser: The :class:`~royalnet.engineer.dispenser.Dispenser` to run the
                          :class:`~royalnet.engineer.conversation.Conversation` in.
        :param conv: The :class:`~royalnet.engineer.conversation.Conversation` to run.
        """

        try:
            async with self.kwargs(conv=conv) as kwargs:
                self.log.debug(f"Running {conv!r} in {dispenser!r}...")
                await dispenser.run(conv=conv, **kwargs)
        except Exception as exception:
            try:
                await self._handle_conversation_exc(dispenser=dispenser, conv=conv, exception=exception)
            except Exception as exception:
                self.log.error(f"Failed to handle conversation exception: {exception!r}")

    @abc.abstractmethod
    async def _handle_conversation_exc(
            self,
            dispenser: "Dispenser",
            conv: "ConversationProtocol",
            exception: Exception
    ) -> None:
        """
        Handle :exc:`Exception`\\ s that were not caught by :class:`~royalnet.engineer.conversation.Conversation`\\ s.

        :param dispenser: The dispenser which hosted the :class:`~royalnet.engineer.conversation.Conversation`\\ .
        :param conv: The :class:`~royalnet.engineer.conversation.Conversation` which didn't catch the error.
        :param exception: The :class:`Exception` that was raised.
        """
        raise NotImplementedError()

    async def _schedule_conversations(self, dispenser: "Dispenser") -> list[asyncio.Task]:
        """
        Schedule the execution of instance of all the :class:`~royalnet.engineer.conversation.Conversation`\\ s listed
        in :attr:`.conversations` in the specified :class:`~royalnet.engineer.dispenser.Dispenser`\\ .

        :param dispenser: The :class:`~royalnet.engineer.dispenser.Dispenser` to run the
                          :class:`~royalnet.engineer.conversation.Conversation`\\ s in.
        :return: The :class:`list` of :class:`asyncio.Task`\\ s that were created.

        .. seealso:: :meth:`._run_conversation`
        """

        if dispenser.locked_by:
            self.log.warning("Tried to run a Conversation in a locked Dispenser!")
            raise LockedDispenserError(
                f"The Dispenser is currently locked and cannot start any new Conversation.",
                dispenser.locked_by
            )

        self.log.info(f"Running in {dispenser!r} all conversations...")

        tasks: list[asyncio.Task] = []
        for conv in self.conversations:

            self.log.debug(f"Creating task for: {conv!r}")
            task = asyncio.create_task(self._run_conversation(dispenser=dispenser, conv=conv))

            tasks.append(task)

        self.log.debug(f"Running a event loop cycle...")
        await asyncio.sleep(0)

        self.log.info(f"Tasks created: {tasks!r}")
        return tasks

    async def put_projectile(self, key: DispenserKey, projectile: "Projectile") -> None:
        """
        Put a :class:`~royalnet.engineer.bullet.projectile.Projectile` in the
        :class:`~royalnet.engineer.dispenser.Dispenser` with the specified key.

        :param key: The key identifying the :class:`~royalnet.engineer.dispenser.Dispenser` among the other
                    :attr:`.dispensers`.
        :param projectile: The :class:`~royalnet.engineer.bullet.projectile.Projectile` to insert.
        """

        self.log.debug(f"Finding dispenser {key!r} to put {projectile!r} in...")
        dispenser = self.get_or_create_dispenser(key=key)

        self.log.debug(f"Running all conversations...")
        await self._schedule_conversations(dispenser=dispenser)

        self.log.debug(f"Putting {projectile!r} in {dispenser!r}...")
        await dispenser.put(projectile)

        self.log.debug(f"Running a event loop cycle...")
        await asyncio.sleep(0)


__all__ = (
    "PDAImplementation",
    "ImplementationException",
    "ImplementationAlreadyBoundError",
    "ConversationListImplementation",
)
