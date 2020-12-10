import functools

from royalnet.royaltyping import *
import pydantic
import inspect
from . import exc


Model = TypeVar("Model")
Value = TypeVar("Value")


class TeleporterConfig(pydantic.BaseConfig):
    """
    A :mod:`pydantic` model config which allows for arbitrary types.
    """
    arbitrary_types_allowed = True


def parameter_to_field(param: inspect.Parameter, **kwargs) -> Tuple[type, pydantic.fields.FieldInfo]:
    """
    Convert a :class:`inspect.Parameter` to a type-field :class:`tuple`, which can be easily passed to
    :func:`pydantic.create_model`.

    If the parameter is already a :class:`pydantic.FieldInfo` (created by :func:`pydantic.Field`), it will be
    returned as the value, without creating a new model.

    :param param: The :class:`inspect.Parameter` to convert.
    :param kwargs: Additional kwargs to pass to the field.
    :return: A :class:`tuple`, where the first element is a :class:`type` and the second is a :class:`pydantic.Field`.
    """
    if isinstance(param.default, pydantic.fields.FieldInfo):
        return (
            param.annotation,
            param.default
        )
    else:
        return (
            param.annotation,
            pydantic.Field(
                default=param.default if param.default is not inspect.Parameter.empty else ...,
                title=param.name,
                **kwargs,
            ),
        )


def signature_to_model(f: Callable,
                       __config__: Type[pydantic.BaseConfig] = TeleporterConfig,
                       extra_params: Dict[str, type] = None) -> Tuple[type, type]:
    """
    Convert the signature of a function to two pydantic models: one for the input and another one for the output.

    Arguments starting with ``_`` are ignored.

    :param f: The function to use the signature of.
    :param __config__: The config the pydantic model should use.
    :param extra_params: Extra parameters to be added to the model.
    :return: A tuple consisting of the input model and the output model.
    """
    if extra_params is None:
        extra_params = {}

    signature: inspect.Signature = inspect.signature(f)

    model_params = {
        key: parameter_to_field(value)
        for key, value in signature.parameters.items()
        if not key.startswith("_")
    }

    input_model = pydantic.create_model(f"{f.__name__}Input",
                                        __config__=TeleporterConfig,
                                        **model_params,
                                        **extra_params)
    output_model = pydantic.create_model(f"{f.__name__}Output",
                                         __config__=TeleporterConfig,
                                         __root__=(signature.return_annotation, pydantic.Field(..., title="Returns")))

    return input_model, output_model


def split_kwargs(**kwargs) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Split the kwargs passed to this function in two different :class:`dict`, based on whether their name starts with
    ``_`` or not.

    :return: A tuple of :class:`dict`, where the second contains the ones starting with ``_``, and the first contains
             the rest.
    """
    model_params = {}
    extra_params = {}
    for key, value in kwargs.items():
        if key.startswith("__"):
            raise ValueError("A keyword argument has a key that starts with __.")
        elif key.startswith("_"):
            extra_params[key] = value
        else:
            model_params[key] = value
    return model_params, extra_params


def teleport_in(__model: type, **kwargs):
    """
    Validate the kwargs passed to this function through the passed :mod:`pydantic` ``__model``.

    :param __model: The model that should be used to validate the kwargs.
    :return: The created model.
    :raises .exc.InputValidationError: If the kwargs fail the validation.
    """
    try:
        return __model(**kwargs)
    except pydantic.ValidationError as e:
        raise exc.InTeleporterError(errors=e.raw_errors, model=e.model)


def teleport_out(__model: type, value: Value) -> Value:
    """
    Validate a single value passed to this function through the ``__root__`` of the passed :mod:`pydantic` ``__model``.

    :param __model: The model that should be used to validate the value.
    :param value: The value that should be validated.
    :return: The value passed as result, after being unwrapped from the created model.
    :raises .exc.OutputValidationError: If the value fails the validation.
    """
    try:
        return __model(__root__=value).__root__
    except pydantic.ValidationError as e:
        raise exc.OutTeleporterError(errors=e.raw_errors, model=e.model)


def teleporter(__config__: Type[pydantic.BaseConfig] = TeleporterConfig,
               is_async: bool = False,
               validate_input: bool = True,
               validate_output: bool = True):
    """
    A factory that returns a decorator which validates a function's passed arguments and its returned value
    using a :mod:`pydantic` model.

    .. warning:: By using this, the function will stop accepting positional arguments, and will only accept
                 keyword arguments.

    :param __config__: The config the pydantic model should use.
    :param is_async: Whether the decorated function is async or not.
    :param validate_input: Whether the input parameters should be validated or not.
    :param validate_output: Whether the return value should be validated or not.
    :return: The decorator to validate the input.

    .. seealso:: :func:`.signature_to_model`
    """
    def decorator(f: Callable):
        # noinspection PyPep8Naming
        InputModel, OutputModel = signature_to_model(f, __config__=__config__)

        if is_async:
            @functools.wraps(f)
            async def decorated(**kwargs):
                if validate_input:
                    model_kwargs, extra_kwargs = split_kwargs(**kwargs)
                    model_kwargs = teleport_in(__model=InputModel, **kwargs).dict()
                    kwargs = {**model_kwargs, **extra_kwargs}
                result = await f(**kwargs)
                if validate_output:
                    result = teleport_out(__model=OutputModel, value=result)
                return result
        else:
            @functools.wraps(f)
            def decorated(**kwargs):
                if validate_input:
                    model_kwargs, extra_kwargs = split_kwargs(**kwargs)
                    model_kwargs = teleport_in(__model=InputModel, **kwargs).dict()
                    kwargs = {**model_kwargs, **extra_kwargs}
                result = f(**kwargs)
                if validate_output:
                    result = teleport_out(__model=OutputModel, value=result)
                return result

        return decorated

    return decorator


__all__ = (
    "TeleporterConfig",
    "parameter_to_field",
    "signature_to_model",
    "teleporter",
)
