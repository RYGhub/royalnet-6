"""
This module contains **bolts**, utility decorators which can be used to enhance
:class:`~royalnet.engineer.conversation.Conversation`\\ s.
"""

from __future__ import annotations
import typing as t

import logging
import sqlalchemy.orm
import functools
import royalnet.lazy

log = logging.getLogger(__name__)


async def use_database(session_class: t.Union[t.Type[sqlalchemy.orm.Session], royalnet.lazy.Lazy], *args, **kwargs):
    """
    Decorator factory which allows a :class:`~royalnet.engineer.conversation.Conversation` to use a
    :class:`sqlalchemy.orm.Session` created from the passed :class:`sqlalchemy.orm.sessionmaker` .

    The session is automatically opened and closed, and will be available in the `_session` kwarg.

    :param session_class: The :class:`sqlalchemy.orm.Session` class to use when creating the session.
                          It can also be provided wrapped in a :class:`royalnet.lazy.Lazy` object, from which it will
                          be evaluated.
    :return: The decorator to use to decorate the function.
    """

    if isinstance(session_class, royalnet.lazy.Lazy):
        session_class = session_class.evaluate()

    def decorator(f):
        @functools.wraps(f)
        async def decorated(**f_kwargs):
            log.debug(f"Opening database session from {session_class!r}...")
            with session_class(*args, **kwargs) as session:
                log.debug(f"Opened database session {session!r} successfully!")
                result = await f(**f_kwargs, _session=session)
                log.debug(f"Closing database session {session!r}...")
            log.debug(f"Closed database session from {session_class!r} successfully!")
            # Shouldn't be necessary, conversations return None anyways
            return result
        return decorated
    return decorator


__all__ = (
    "use_database",
)
