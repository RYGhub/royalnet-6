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


class NotSupportedError(BulletException, NotImplementedError):
    """
    The requested property isn't available on the current frontend.
    """
