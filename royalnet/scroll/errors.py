from ..errors import RoyalnetException


class ScrollException(RoyalnetException):
    """An exception raised by the Scroll module."""


class NotFoundError(ScrollException):
    """The requested config key was not found."""


class InvalidFormatError(ScrollException):
    """The requested config key is not valid."""


class ParseError(ScrollException):
    """The config value could not be parsed correctly."""


class InvalidFileType(ParseError):
    """The type of the specified config file is not currently supported."""


__all__ = (
    "ScrollException",
    "NotFoundError",
    "InvalidFormatError",
    "ParseError",
    "InvalidFileType",
)
