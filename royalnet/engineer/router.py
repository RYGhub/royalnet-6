import functools
import pydantic
from royalnet.royaltyping import *
from . import params


class EngineerRouter:
    """
    A class that handles the registration and call of commands and the validation of their parameters.
    """

    def __init__(self):
        self.commands = {}

    def add_command(self, f: Callable, name: Optional[str]):
        """
        Add a command to the router.

        :param name: The name of the command (``start``, ``settings``, etc). If not specified, it will use the name
                     of the wrapped function.
        :param f: The function that should be executed when the command is called. It must have a ``.model`` property.

        .. seealso:: :meth:`.command`, :func:`.params.function_with_model`
        """
        name = name if name else f.__name__
        f._model = params.signature_to_model(f)
        self.commands[name] = f

    def command(self, name: Optional[str] = None):
        """
        A decorator factory to add a command to the router.

        .. code-block:: python

           @command()
           def ping():
               print("Pong!")

        .. code-block:: python

           @command(name="ping")
           def xyzzy():
               print("Pong!")

        :param name: The name of the command (``start``, ``settings``, etc). If not specified, it will use the name
                     of the wrapped function.
        :return: The decorated function.

        .. seealso:: :meth:`.add_command`
        """

        def decorator(f: Callable):

            @functools.wraps(f)
            @params.function_with_model()
            def decorated(*args, **kwargs):
                return f(*args, **kwargs)

            self.add_command(f=decorated, name=name)
            return decorated

        return decorator

    def call(self, __name: str, **kwargs):
        model_params = {}
        extra_params = {}
        for key, value in kwargs.items():
            if key.startswith("_"):
                extra_params[key] = value
            else:
                model_params[key] = value

        f = self.commands[__name]
        # noinspection PyPep8Naming
        Model: Type[pydantic.BaseModel] = f.model
        model: pydantic.BaseModel = Model(**model_params)
        return f(**model.dict(), **extra_params)


__all__ = (
    "EngineerRouter",
)
