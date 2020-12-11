import royalnet.exc
import pydantic


class EngineerException(royalnet.exc.RoyalnetException):
    """
    An exception raised by the engineer module.
    """


class BlueprintError(EngineerException):
    """
    An error related to the :mod:`royalnet.engineer.blueprints`.
    """


class NeverAvailableError(BlueprintError, NotImplementedError):
    """
    The requested property is never supplied by the chat platform the message was sent in.
    """

    priority = 1


class NotAvailableError(BlueprintError):
    """
    The requested property was not supplied by the chat platform for the specific message this exception was raised in.
    """

    priority = 2


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
