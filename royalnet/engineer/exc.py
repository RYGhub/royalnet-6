import pydantic


class EngineerException(Exception):
    pass


class WrenchException(EngineerException):
    pass


class DeliberateException(WrenchException):
    """
    This exception was deliberately raised by :class:`royalnet.engineer.wrench.ErrorAll`
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