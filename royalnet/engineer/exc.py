import royalnet.exc
import pydantic


class EngineerException(royalnet.exc.RoyalnetException):
    """
    An exception raised by the engineer module.
    """


class TeleporterError(EngineerException, pydantic.ValidationError):
    """
    The validation of some object though a :mod:`pydantic` model failed.
    """


class InTeleporterError(TeleporterError):
    """
    The input parameters validation failed.
    """


class OutTeleporterError(TeleporterError):
    """
    The return value validation failed.
    """
