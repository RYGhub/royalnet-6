from ..exc import RoyalnetException


class ScrollsException(RoyalnetException):
    """An exception raised by the scrolls module."""


class NotFoundError(ScrollsException, KeyError):
    """The requested config key was not found."""


class MissingConfigFileError(ScrollsException, IOError):
    """The config file does not exist, and ``require_file`` is set to :data:`True`."""


class InvalidFormatError(ScrollsException):
    """The requested config key is not valid."""


class ParseError(ScrollsException):
    """The config value could not be parsed correctly."""


class InvalidFileType(ParseError):
    """The type of the specified config file is not currently supported."""


__all__ = (
    "ScrollsException",
    "NotFoundError",
    "MissingConfigFileError",
    "InvalidFormatError",
    "ParseError",
    "InvalidFileType",
)
