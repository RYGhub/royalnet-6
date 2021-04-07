"""
This module contains the :class:`.Teleporter` class and its exceptions.
"""

from __future__ import annotations
import royalnet.royaltyping as t

import logging
import pydantic
import inspect

from . import exc

Value = t.TypeVar("Value")
log = logging.getLogger(__name__)


class TeleporterError(exc.EngineerException, pydantic.ValidationError):
    """
    The base class for errors in :mod:`royalnet.engineer.teleporter`.
    """


class InTeleporterError(TeleporterError):
    """
    The input parameters validation failed.
    """


class OutTeleporterError(TeleporterError):
    """
    The return value validation failed.
    """


class Teleporter:
    """
    A :class:`.Teleporter` is a function wrapper which uses :mod:`pydantic` to perform type checking
    """

    def __init__(self,
                 f: t.Callable[..., t.Any],
                 validate_input: bool = True,
                 validate_output: bool = True):
        self.f: t.Callable = f
        """
        The function which is having its parameters and return value validated.
        """

        self.InputModel: t.Type[pydantic.BaseModel] = self._create_input_model() if validate_input else None
        """
        The :mod:`pydantic` model used to validate input parameters.
        """

        self.OutputModel: t.Type[pydantic.BaseModel] = self._create_output_model() if validate_output else None
        """
        The :mod:`pydantic` model used to validate the return value.
        """

    def __repr__(self):
        if self.InputModel and self.OutputModel:
            validation = "validating input and output"
        elif self.InputModel:
            validation = "validating only input"
        elif self.OutputModel:
            validation = "validating only output"
        else:
            validation = "not validating anything"
        return f"<{self.__class__.__qualname__} {validation}>"

    @staticmethod
    def _parameter_to_field(param: inspect.Parameter, **kwargs) -> t.Tuple[type, pydantic.fields.FieldInfo]:
        """
        Convert a :class:`inspect.Parameter` to a type-field :class:`tuple`, which can be easily passed to
        :func:`pydantic.create_model`.

        If the parameter is already a :class:`pydantic.FieldInfo` (created by :func:`pydantic.Field`), it will be
        returned as the value, without creating a new model.

        :param param: The :class:`inspect.Parameter` to convert.
        :param kwargs: Additional kwargs to pass to the field.
        :return: A :class:`tuple`, where the first element is a :class:`type` and the second is a
                 :class:`pydantic.Field`.
        """
        if isinstance(param.default, pydantic.fields.FieldInfo):
            log.debug(f"Parameter {param} is a pydantic.Field, leaving it untouched...")
            return (
                param.annotation,
                param.default
            )
        else:
            log.debug(f"Parameter {param} is not a pydantic.Field, converting it to one...")
            return (
                param.annotation,
                pydantic.Field(
                    default=param.default if param.default is not inspect.Parameter.empty else ...,
                    title=param.name,
                    **kwargs,
                ),
            )

    class TeleporterDefaultConfig(pydantic.BaseConfig):
        """
        A :mod:`pydantic` model config which allows for arbitrary types.
        """
        arbitrary_types_allowed = True

    def get_model_config(self):
        """
        Get the :mod:`pydantic` config to use in both input and output, if :meth:`.get_input_model_config` and
        :meth:`.get_output_model_config` are not overridden.

        :return: A :mod:`pydantic` config.
        """
        log.debug("Getting default model config...")
        return self.TeleporterDefaultConfig

    def get_input_model_config(self):
        """
        Get the :mod:`pydantic` config to use while creating input models.

        :return: A :mod:`pydantic` config.
        """
        log.debug("Getting common model config...")
        return self.get_model_config()

    def get_output_model_config(self):
        """
        Get the :mod:`pydantic` config to use while creating output models.

        :return: A :mod:`pydantic` config.
        """
        log.debug("Getting common model config...")
        return self.get_model_config()

    def _create_input_model(self,
                            **extra_fields) -> t.Type[pydantic.BaseModel]:
        """
        Create a pydantic model based on the arguments of the :attr:`f` function.

        Arguments starting with ``_`` are ignored.

        The model is created using the config obtained through :meth:`.get_input_model_config` .

        :param extra_fields: Extra fields to be added to the model.
        :return: The created pydantic model.
        """
        log.debug(f"Getting function signature of: {self.f!r}")
        signature: inspect.Signature = inspect.signature(self.f)

        log.debug(f"Converting parameter annotations of {self.f!r} to fields...")
        fields = {
            key: self._parameter_to_field(value)
            for key, value in signature.parameters.items()
            if not key.startswith("_")
        }

        log.debug(f"Creating input model with parsed fields {fields!r} and extra fields {extra_fields!r}...")
        return pydantic.create_model(
            f"{self.__class__.__name__}InputModel",
            __config__=self.get_input_model_config(),
            **fields,
            **extra_fields
        )

    def _create_output_model(self) -> t.Type[pydantic.BaseModel]:
        """
        Create a pydantic model based on the return value of the :attr:`f` function.

        The model is created using the config obtained through :meth:`.get_output_model_config` .

        :return: The created pydantic model.
        """
        log.debug(f"Getting function signature of: {self.f!r}")
        signature: inspect.Signature = inspect.signature(self.f)

        log.debug(f"Creating output model...")
        return pydantic.create_model(
            f"{self.__class__.__name__}OutputModel",
            __config__=self.get_output_model_config(),
            __root__=(signature.return_annotation, pydantic.Field(..., title="Returns"))
        )

    def teleport_in(self, **kwargs) -> pydantic.BaseModel:
        """
        Instantiate the :attr:`.InputModel` with the passed kwargs.

        :param kwargs: The keyword arguments that should be passed to the model.
        :return: The created model.
        :raises .InTeleporterError: If the kwargs fail the validation.
        """
        log.debug(f"Teleporting in: {kwargs!r}")
        try:
            return self.InputModel(**kwargs)
        except pydantic.ValidationError as e:
            log.error(f"Teleport in failed: {e!r}")
            raise InTeleporterError(errors=e.raw_errors, model=e.model)

    def teleport_out(self, value: Value) -> pydantic.BaseModel:
        """
        Instantiate the :attr:`.OutputModel` with the passed value.

        :param value: The value that should be validated.
        :return: The created model.
        :raises .OutTeleporterError: If the value fails the validation.
        """
        log.debug(f"Teleporting out: {value!r}")
        try:
            return self.OutputModel(__root__=value)
        except pydantic.ValidationError as e:
            log.error(f"Teleport out failed: {e!r}")
            raise OutTeleporterError(errors=e.raw_errors, model=e.model)

    @staticmethod
    def _split_kwargs(**kwargs) -> t.Tuple[t.Dict[str, t.Any], t.Dict[str, t.Any]]:
        """
        Split the passed kwargs in two different :class:`dict`:
        - One containing the arguments that **do not start with ``_``**;
        - Another containing the ones which do.

        :return: A tuple of :class:`dict`, where the second contains the ones starting with ``_``, and the first
                 contains the rest.
        """
        model_params = {}
        extra_params = {}
        for key, value in kwargs.items():
            if key.startswith("_"):
                log.debug(f"Found extra keyword argument: {key}")
                extra_params[key] = value
            else:
                log.debug(f"Found model keyword argument: {key}")
                model_params[key] = value
        return model_params, extra_params

    def _run(self, **kwargs) -> t.Any:
        """
        Run the :class:`.Teleporter` synchronously.
        """
        if self.InputModel:
            log.debug("Validating input...")
            model_kwargs, extra_kwargs = self._split_kwargs(**kwargs)
            model_kwargs = self.teleport_in(**kwargs).dict()
            kwargs = {**model_kwargs, **extra_kwargs}
        result = self.f(**kwargs)
        if self.OutputModel:
            result = self.teleport_out(result).__root__
        return result

    async def _run_async(self, **kwargs) -> t.Awaitable[t.Any]:
        """
        Run the :class:`.Teleporter` asynchronously.
        """
        if self.InputModel:
            log.debug("Validating input...")
            model_kwargs, extra_kwargs = self._split_kwargs(**kwargs)
            model_kwargs = self.teleport_in(**kwargs).dict()
            kwargs = {**model_kwargs, **extra_kwargs}
        result = await self.f(**kwargs)
        if self.OutputModel:
            result = self.teleport_out(result).__root__
        return result

    def __call__(self, **kwargs) -> t.Any:
        if inspect.iscoroutinefunction(self.f):
            return self._run_async(**kwargs)
        else:
            return self._run(**kwargs)


__all__ = (
    "InTeleporterError",
    "OutTeleporterError",
    "Teleporter",
    "TeleporterError",
)
