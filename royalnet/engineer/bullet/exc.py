"""
The exceptions which can happen in bullets.
"""

from .. import exc


class BulletException(exc.EngineerException):
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
