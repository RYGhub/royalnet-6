from royalnet.royaltyping import *
import pydantic
import inspect


class ModelConfig(pydantic.BaseConfig):
    """
    A :mod:`pydantic` model config which allows for arbitrary royaltyping.
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


def signature_to_model(f: Callable, __config__: pydantic.BaseConfig = ModelConfig, **extra_params):
    """
    Convert the signature of a async function to a pydantic model.

    Arguments starting with ``_`` are ignored.

    :param f: The async function to use the signature of.
    :param __config__: The config the pydantic model should use.
    :param extra_params: Extra parameters to be added to the model.
    :return: The created pydantic model.
    """
    name: str = f.__name__
    signature: inspect.Signature = inspect.signature(f)

    params = {key: parameter_to_field(value) for key, value in signature.parameters.items() if not key.startswith("_")}

    model = pydantic.create_model(name,
                                  __config__=ModelConfig,
                                  **params,
                                  **extra_params)
    return model


def function_with_model(__config__: pydantic.BaseConfig = ModelConfig, **extra_params):
    """
    A decorator that adds the property ``.model`` to the wrapped function.

    :param __config__: The config the pydantic model should use.
    :param extra_params: Extra parameters to be added to the model.
    """
    def decorator(f: Callable):
        f.model = signature_to_model(f, __config__=__config__, **extra_params)
        return f
    return decorator


__all__ = (
    "ModelConfig",
    "parameter_to_field",
    "signature_to_model",
    "function_with_model",
)
