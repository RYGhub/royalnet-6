"""
.. todo:: Document this.
"""

import royalnet.royaltyping as t
import abc
import contextlib
import asyncio

if t.TYPE_CHECKING:
    from royalnet.engineer.conversation import ConversationProtocol
    from royalnet.engineer.dispenser import Dispenser
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

    def __repr__(self):
        return f"<PDAImplementation {self.name}>"

    def __str__(self):
        return self.name

    def bind(self, pda: "PDA") -> None:
        """
        .. todo:: Document this.
        """

        if self.bound_to is not None:
            raise ImplementationAlreadyBound()
        self.bound_to = pda

    @abc.abstractmethod
    @property
    def namespace(self):
        """
        .. todo:: Document this.
        """

        raise NotImplementedError()


class ImplementationException(Exception):
    """
    .. todo:: Document this.
    """


class ImplementationAlreadyBound(ImplementationException):
    """
    .. todo:: Document this.
    """


class ConversationListImplementation(PDAImplementation, metaclass=abc.ABCMeta):
    """
    A :class:`.PDAImplementation` which instantiates multiple :class:`~royalnet.engineer.conversation.Conversation`\\ s
    before putting a :class:`~royalnet.engineer.bullet.projectile.Projectile` in a
    :class:`~royalnet.engineer.dispenser.Dispenser` .
    """

    def __init__(self, name: str):
        super().__init__(name)

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

        return []

    def _create_dispensers(self) -> dict[t.Any, "Dispenser"]:
        """
        Create the :attr:`.dispensers` dictionary of the PDA.

        :return: The created dictionary (empty by default).
        """

        return {}

    def get_dispenser(self, key: "DispenserKey") -> t.Optional["Dispenser"]:
        """
        Get a :class:`~royalnet.engineer.dispenser.Dispenser` from :attr:`.dispenser` knowing its key.

        :param key: The key to get the dispenser with.
        :return: The retrieved dispenser.

        .. seealso:: :meth:`dict.get`
        """

        return self.dispensers.get(key)

    def _create_dispenser(self) -> "Dispenser":
        """
        Create a new dispenser.

        :return: The created dispenser.
        """

        return Dispenser()

    def get_or_create_dispenser(self, key: "DispenserKey") -> "Dispenser":
        """
        .. todo:: Document this.
        """

        if key not in self.dispensers:
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

        default_kwargs = {
            "_pda": self.bound_to,
            "_imp": self,
            "_conv": conv,
        }

        async with self._kwargs(default_kwargs, self.extensions) as kwargs:
            yield kwargs

    @contextlib.asynccontextmanager
    async def _kwargs(self, kwargs: t.Kwargs, remaining: list["PDAExtension"]) -> t.Kwargs:
        """
        .. todo:: Document this.
        """

        extension: "PDAExtension" = remaining.pop(0)

        async with extension.kwargs(kwargs) as kwargs:
            if not remaining:
                yield kwargs
            else:
                async with self._kwargs(kwargs=kwargs, remaining=remaining) as kwargs:
                    yield kwargs

    def register_conversation(self, conversation: "ConversationProtocol") -> None:
        """
        Register a new :class:`~royalnet.engineer.conversation.Conversation` to be run when a new
        :class:`~royalnet.engineer.bullet.projectile.Projectile` is :meth:`.put`\\ .

        :param conversation: The :class:`~royalnet.engineer.conversation.Conversation` to register.
        """

        self.conversations.append(conversation)

    def unregister_conversation(self, conversation: "ConversationProtocol") -> None:
        """
        Unregister a :class:`~royalnet.engineer.conversation.Conversation`, stopping it from being run when a new
        :class:`~royalnet.engineer.bullet.projectile.Projectile` is :meth:`.put`\\ .

        :param conversation: The :class:`~royalnet.engineer.conversation.Conversation` to unregister.
        """

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
        .. todo:: Document this.
        """

        async with self.kwargs(conv=conv) as kwargs:
            await dispenser.run(conv=conv, **kwargs)

    def _run_all_conversations(self, dispenser: "Dispenser") -> list[asyncio.Task]:
        """
        .. todo:: Document this.
        """

        tasks: list[asyncio.Task] = []
        for conv in self.conversations:
            task = asyncio.create_task(self._run_conversation(dispenser=dispenser, conv=conv))
            tasks.append(task)
        await asyncio.sleep(0)
        return tasks

    async def put_projectile(self, key: DispenserKey, projectile: "Projectile") -> None:
        """
        Put a :class:`~royalnet.engineer.bullet.projectile.Projectile` in the
        :class:`~royalnet.engineer.dispenser.Dispenser` with the specified key.

        :param key: The key identifying the :class:`~royalnet.engineer.dispenser.Dispenser` among the other
                    :attr:`.dispensers`.
        :param projectile: The :class:`~royalnet.engineer.bullet.projectile.Projectile` to insert.
        """

        dispenser = self.get_or_create_dispenser(key=key)
        self._run_all_conversations(dispenser=dispenser)
        await dispenser.put(projectile)
        await asyncio.sleep(0)


__all__ = (
    "PDAImplementation",
    "ImplementationException",
    "ImplementationAlreadyBound",
    "ConversationListImplementation",
)
