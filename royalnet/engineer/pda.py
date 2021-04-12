import abc
import asyncio
import contextlib
import sqlalchemy.orm
import sqlalchemy.engine
import royalnet.royaltyping as t

if t.TYPE_CHECKING:
    from royalnet.engineer.dispenser import Dispenser
    from royalnet.engineer.conversation import ConversationProtocol
    from royalnet.engineer.bullet.projectiles import Projectile
    from royalnet.engineer.command import PartialCommand, FullCommand
    DispenserKey = t.TypeVar("DispenserKey")


class PDA(metaclass=abc.ABCMeta):
    """
    A :class:`.PDA` is an implementation of the :mod:`royalnet.engineer` stack for a specific chat platform.

    This is the :class:`abc.ABC` that new PDAs should use to implement their chat platform features.
    """

    def __init__(self):
        self.dispensers: dict["DispenserKey", "Dispenser"] = self._create_dispensers()

    def __repr__(self):
        return f"<{self.__class__.__qualname__} ({len(self.dispensers)} dispensers)>"

    def _create_dispensers(self) -> dict[t.Any, "Dispenser"]:
        """
        Create the :attr:`.dispensers` dictionary of the PDA.

        :return: The created dictionary (empty by default).
        """

        return {}

    def _get_dispenser(self, key: "DispenserKey") -> t.Optional["Dispenser"]:
        """
        Get a :class:`~royalnet.engineer.dispenser.Dispenser` from :attr:`.dispenser` knowing its key.

        :param key: The key to get the dispenser with.
        :return: The retrieved dispenser.

        .. seealso:: :meth:`dict.get`
        """

        return self.dispensers.get(key)

    def _make_dispenser(self) -> "Dispenser":
        """
        Create a new dispenser.

        :return: The created dispenser.
        """

        return Dispenser()

    async def _hook_pre_put(self, key: "DispenserKey", dispenser, projectile) -> bool:
        """
        **Hook** called before putting a :class:`~royalnet.engineer.bullet.projectile.Projectile` in a
        :class:`~royalnet.engineer.dispenser.Dispenser`.

        :param key: The key identifying the :class:`~royalnet.engineer.dispenser.Dispenser` among the other
                    :attr:`.dispensers`.
        :param dispenser: The :class:`~royalnet.engineer.dispenser.Dispenser` the projectile is being
                          :class:`~royalnet.engineer.dispenser.Dispenser.put` in.
        :param projectile: The :class:`~royalnet.engineer.bullet.projectile.Projectile` which is being inserted.
        :return: A :class:`bool`, which will cancel the :meth:`.put` if is :data:`False`.
        """

        pass

    async def _hook_post_put(self, key, dispenser, projectile) -> None:
        """
        **Hook** called after putting a :class:`~royalnet.engineer.bullet.projectile.Projectile` in a
        :class:`~royalnet.engineer.dispenser.Dispenser`.

        :param key: The key identifying the :class:`~royalnet.engineer.dispenser.Dispenser` among the other
                    :attr:`.dispensers`.
        :param dispenser: The :class:`~royalnet.engineer.dispenser.Dispenser` the projectile was
                          :class:`~royalnet.engineer.dispenser.Dispenser.put` in.
        :param projectile: The :class:`~royalnet.engineer.bullet.projectile.Projectile` which was inserted.
        """

        pass

    async def _asyncio_step(self) -> None:
        """
        Perform an iteration of the event loop.

        Equivalent to ``asyncio.sleep(0)``.
        """

        await asyncio.sleep(0)

    async def put(self, key: "DispenserKey", projectile: "Projectile") -> None:
        """
        Put a :class:`~royalnet.engineer.bullet.projectile.Projectile` in the
        :class:`~royalnet.engineer.dispenser.Dispenser` with the specified key.

        :param key: The key identifying the :class:`~royalnet.engineer.dispenser.Dispenser` among the other
                    :attr:`.dispensers`.
        :param projectile: The :class:`~royalnet.engineer.bullet.projectile.Projectile` to insert.

        .. seealso:: :meth:`._hook_pre_put`\\ , :meth:`.hook_post_put`
        """

        dispenser = self._get_dispenser(key)

        if dispenser is None:
            dispenser = self._make_dispenser()
            self.dispensers[key] = dispenser

        go_on = await self._hook_pre_put(key=key, dispenser=dispenser, projectile=projectile)
        await self._asyncio_step()

        if go_on:
            return

        await dispenser.put(projectile)
        await self._asyncio_step()

        await self._hook_post_put(key=key, dispenser=dispenser, projectile=projectile)
        await self._asyncio_step()


class ConversationListPDA(PDA, metaclass=abc.ABCMeta):
    """
    A :class:`.PDA` which instantiates multiple :class:`~royalnet.engineer.conversation.Conversation`\\ s before putting
    a :class:`~royalnet.engineer.bullet.projectile.Projectile` in a :class:`~royalnet.engineer.dispenser.Dispenser` .
    """

    def __init__(self, conversation_kwargs: dict[str, t.Any]):
        super().__init__()
        self.conversations: list["ConversationProtocol"] = self._create_conversations()
        self.conversation_kwargs: dict[str, t.Any] = conversation_kwargs
        self._conversation_coro: list[t.Awaitable[t.Any]] = []

    def _create_conversations(self) -> list["ConversationProtocol"]:
        """
        Create the :attr:`.conversations` :class:`list` of the :class:`.ConversationListPDA`\\ .

        :return: The created :class:`list`\\ .
        """

        return []

    @contextlib.asynccontextmanager
    async def _conversation_kwargs(self, conv: "ConversationProtocol") -> dict[str, t.Any]:
        """
        :func:`contextlib.asynccontextmanager` factory which yields the arguments to pass to newly created
        :class:`~royalnet.engineer.conversation.Conversation`\\ s .

        By default, the following arguments are passed:
        - ``_pda``: contains this :class:`.PDA`
        - ``_conv``: contains the :class:`~royalnet.engineer.conversation.Conversation` which was just created.

        :param conv: The :class:`~royalnet.engineer.conversation.Conversation` to create the args for.
        :return: The corresponding :func:`contextlib.asynccontextmanager`\\ .
        """

        yield {
            "_pda": self,
            "_conv": conv,
            **self.conversation_kwargs,
        }

    async def _run_conversation(self, dispenser: "Dispenser", conv: "ConversationProtocol", **override_kwargs) -> None:
        """
        Run a :class:`~royalnet.engineer.conversation.Conversation` with its proper kwargs.

        :param dispenser: The :class:`~royalnet.engineer.dispenser.Dispenser` to run the
                          :class:`~royalnet.engineer.conversation.Conversation` in.
        :param conv: The :class:`~royalnet.engineer.conversation.Conversation` to run.
        :param override_kwargs: Kwargs to be passed to the conversation in addition to the ones generated by
                                :meth:`_conversation_kwargs`\\ .
        """
        async with self._conversation_kwargs(conv=conv) as default_kwargs:
            coro = dispenser.run(conv, **default_kwargs, **override_kwargs)

            self._conversation_coro.append(coro)
            try:
                await coro
            finally:
                self._conversation_coro.remove(coro)

    async def _hook_pre_put(self, key, dispenser, projectile):
        await super()._hook_pre_put(key=key, dispenser=dispenser, projectile=projectile)
        for conv in self.conversations:
            asyncio.create_task(self._run_conversation(dispenser=dispenser, conv=conv))

    async def _hook_post_put(self, key, dispenser, projectile):
        await super()._hook_post_put(key=key, dispenser=dispenser, projectile=projectile)

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
    def _make_partialcommand_pattern(self, partial: "PartialCommand") -> str:
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

        return partial.complete(names=names, pattern=self._make_partialcommand_pattern(partial))

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


class WithDatabaseSession(ConversationListPDA, metaclass=abc.ABCMeta):
    """
    A :class:`.ConversationListPDA` with database support provided by :mod:`sqlalchemy`\\ by extending
    :meth:`._conversation_kwargs` with the ``_session`` kwarg.
    """

    def __init__(self, engine: sqlalchemy.engine.Engine, conversation_kwargs: dict[str, t.Any]):
        super().__init__(conversation_kwargs)
        self.engine: sqlalchemy.engine.Engine = engine
        self.Session: sqlalchemy.orm.sessionmaker = sqlalchemy.orm.sessionmaker(bind=self.engine)

    @contextlib.asynccontextmanager
    async def _conversation_kwargs(self, conv: "ConversationProtocol") -> dict[str, t.Any]:

        with self.Session(future=True) as session:

            yield {
                "_pda": self,
                "_conv": conv,
                "_session": session,
                **self.conversation_kwargs,
            }


__all__ = (
    "PDA",
    "ConversationListPDA",
    "WithDatabaseSession",
)
