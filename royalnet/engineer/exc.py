import royalnet.exc
import pydantic


class EngineerException(royalnet.exc.RoyalnetException):
    """
    An exception raised by the engineer module.
    """


class ValidationError(EngineerException, pydantic.ValidationError):
    """
    The validation of some object though a :mod:`pydantic` model failed.
    """


class InputValidationError(ValidationError):
    """
    The input parameters validation failed.
    """


class OutputValidationError(ValidationError):
    """
    The return value validation failed.
    """