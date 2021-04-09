import abc
import asyncio
import royalnet.royaltyping as t

if t.TYPE_CHECKING:
    from royalnet.engineer.dispenser import Dispenser
    from royalnet.engineer.conversation import ConversationProtocol
    from royalnet.engineer.bullet.projectiles import Projectile
    from royalnet.engineer.command import PartialCommand, FullCommand
    DispenserKey = t.TypeVar("DispenserKey")


class PDA(metaclass=abc.ABCMeta):
    def __init__(self):
        self.dispensers: dict["DispenserKey", "Dispenser"] = self._create_dispensers()

    def __repr__(self):
        return f"<{self.__class__.__qualname__} ({len(self.dispensers)} dispensers)>"

    def _create_dispensers(self) -> dict[t.Any, "Dispenser"]:
        return {}

    def _get_dispenser(self, key: "DispenserKey") -> t.Optional["Dispenser"]:
        return self.dispensers.get(key)

    def _make_dispenser(self):
        return Dispenser()

    async def _hook_pre_put(self, key, dispenser, projectile):
        pass

    async def _hook_post_put(self, key, dispenser, projectile):
        pass

    async def _asyncio_step(self):
        await asyncio.sleep(0)

    async def put(self, key: "DispenserKey", projectile: "Projectile") -> None:
        dispenser = self._get_dispenser(key)

        if dispenser is None:
            dispenser = self._make_dispenser()
            self.dispensers[key] = dispenser

        await self._hook_pre_put(key=key, dispenser=dispenser, projectile=projectile)
        await self._asyncio_step()

        await dispenser.put(projectile)
        await self._asyncio_step()

        await self._hook_post_put(key=key, dispenser=dispenser, projectile=projectile)
        await self._asyncio_step()


class ConversationListStrategy(PDA, metaclass=abc.ABCMeta):
    def __init__(self, conversation_kwargs: dict[str, t.Any]):
        super().__init__()
        self.conversations: list["ConversationProtocol"] = self._create_conversations()
        self.conversation_kwargs: dict[str, t.Any] = conversation_kwargs
        self._conversation_tasks: list[asyncio.Task] = []

    def _create_conversations(self) -> list["ConversationProtocol"]:
        return []

    def _make_conversation_kwargs(self, conversation: "ConversationProtocol") -> dict[str, t.Any]:
        return {
            "_pda": self,
            "_conv": self,  # FIXME: this is either genius or crazy
            **self.conversation_kwargs,
        }

    def _create_task(self, coro):
        loop = asyncio.get_running_loop()
        task = loop.create_task(coro)
        self._conversation_tasks.append(task)
        return task

    def _start_conversation(self, dispenser: "Dispenser", conversation: "ConversationProtocol") -> asyncio.Task:
        coro = dispenser.run(conversation, **self._make_conversation_kwargs(conversation))
        return self._create_task(coro)

    def _cleanup_conversation_tasks(self):
        for task in self._conversation_tasks:
            # TODO: done includes exception?
            if task.done() or task.exception():
                self._conversation_tasks.remove(task)

    async def _hook_pre_put(self, key, dispenser, projectile):
        await super()._hook_pre_put(key=key, dispenser=dispenser, projectile=projectile)
        for conversation in self.conversations:
            self._start_conversation(dispenser=dispenser, conversation=conversation)

    async def _hook_post_put(self, key, dispenser, projectile):
        await super()._hook_post_put(key=key, dispenser=dispenser, projectile=projectile)
        self._cleanup_conversation_tasks()

    def register_conversation(self, conversation: "ConversationProtocol") -> None:
        self.conversations.append(conversation)

    def unregister_conversation(self, conversation: "ConversationProtocol") -> None:
        self.conversations.remove(conversation)

    @abc.abstractmethod
    def _make_partialcommand_pattern(self, partial: "PartialCommand"):
        raise NotImplementedError()

    def complete_partialcommand(self, partial: "PartialCommand", names: list[str]) -> "FullCommand":
        return partial.complete(names=names, pattern=self._make_partialcommand_pattern(partial))

    def register_partialcommand(self, partial: "PartialCommand", names: list[str]) -> "FullCommand":
        full = self.complete_partialcommand(partial=partial, names=names)
        self.register_conversation(full)
        return full


__all__ = (
    "PDA",
    "ConversationListStrategy",
)
