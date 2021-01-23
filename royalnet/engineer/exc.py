import pydantic


class EngineerException(Exception):
    """
    The base class for errors in :mod:`royalnet.engineer`.
    """


class WrenchException(EngineerException):
    """
    The base class for errors in :mod:`royalnet.engineer.wrench`.
    """


class DeliberateException(WrenchException):
    """
    This exception was deliberately raised by :class:`royalnet.engineer.wrench.ErrorAll`.
    """


class TeleporterError(EngineerException, pydantic.ValidationError):
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


class BulletException(EngineerException):
    """
    The base class for errors in :mod:`royalnet.engineer.bullet`.
    """


class FrontendError(BulletException):
    """
    An error occoured while performing a frontend operation, such as sending a message.
    """


class NotSupportedError(FrontendError, NotImplementedError):
    """
    The requested property isn't available on the current frontend.
    """


class ForbiddenError(FrontendError):
    """
    The bot user does not have sufficient permissions to perform a frontend operation.
    """


class DispenserException(EngineerException):
    """
    The base class for errors in :mod:`royalnet.engineer.dispenser`.
    """


class LockedDispenserError(DispenserException):
    """
    The dispenser couldn't start a new conversation as it is currently locked.
    """
    def __init__(self, locked_by, *args):
        super().__init__(*args)
        self.locked_by = locked_by


__all__ = (
    "EngineerException",
    "WrenchException",
    "DeliberateException",
    "TeleporterError",
    "InTeleporterError",
    "OutTeleporterError",
    "BulletException",
    "FrontendError",
    "NotSupportedError",
    "ForbiddenError",
    "DispenserException",
    "LockedDispenserError",
)
