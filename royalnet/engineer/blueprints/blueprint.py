import abc

from .. import exc


class Blueprint(metaclass=abc.ABCMeta):
    """
    A class containing methods common between all blueprints.

    To extend a blueprint, inherit from it while using the :class:`abc.ABCMeta` metaclass, and make all new functions
    return :exc:`.exc.NeverAvailableError`:

    .. code-block::

       class Channel(Blueprint, metaclass=abc.ABCMeta):
           def name(self):
               raise exc.NeverAvailableError()

    To implement a blueprint for a specific chat platform, inherit from the blueprint, override :meth:`__init__`,
    :meth:`__hash__` and the methods that are implemented by the platform in question, either returning the
    corresponding value or raising :exc:`.exc.NotAvailableError` if there is no data available.

    .. code-block::

       class ExampleChannel(Channel):
           def __init__(self, chat_id: int):
               self.chat_id: int = chat_id

           def __hash__(self):
               return self.chat_id

           def name(self):
               return ExampleClient.expensive_get_channel_name(self.chat_id)

    .. note:: To improve performance, you might want to wrap all data methods in :func:`functools.lru_cache` decorators.

              .. code-block::

                 @functools.lru_cache(24)
                 def name(self):
                     return ExampleClient.expensive_get_channel_name(self.chat_id)

    """

    def __init__(self):
        """
        :return: The created object.
        """
        pass

    @abc.abstractmethod
    def __hash__(self):
        """
        :return: A value that uniquely identifies the channel inside this Python process.
        """
        raise NotImplementedError()

    def requires(self, *fields) -> True:
        """
        Ensure that this blueprint has the specified fields, re-raising the highest priority exception raised between
        all of them.

        .. code-block::

            def print_msg(message: Message):
                message.requires(Message.text, Message.timestamp)
                print(f"{message.timestamp().isoformat()}: {message.text()}")

        :raises .exc.NeverAvailableError: If at least one of the fields raised a :exc:`.exc.NeverAvailableError`.
        :raises .exc.NotAvailableError: If no field raised a :exc:`.exc.NeverAvailableError`, but at least one raised a
                                        :exc:`.exc.NotAvailableError`.
        """

        exceptions = []

        for field in fields:
            try:
                field(self)
            except exc.NeverAvailableError as ex:
                exceptions.append(ex)
            except exc.NotAvailableError as ex:
                exceptions.append(ex)

        if len(exceptions) > 0:
            raise max(exceptions, key=lambda e: e.priority)

        return True


__all__ = (
    "Blueprint",
)
