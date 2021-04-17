"""
This module contains the :class:`~royalnet.engineer.pda.extensions.base.PDAExtension`\\ s that allow
:class:`~royalnet.engineer.conversation.Conversation`\\ s to access a database.
"""

import royalnet.royaltyping as t
import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.asyncio as sea
import contextlib
import logging

from . import base

log = logging.getLogger(__name__)


class SQLAlchemyExtension(base.PDAExtension):
    """
    Extends a :class:`~royalnet.engineer.pda.implementations.base.PDAImplementation` by adding a :mod:`sqlalchemy`
    session to conversations through the ``_session`` kwarg.
    """

    def __init__(self, engine: sqlalchemy.engine.Engine, session_kwargs: t.Kwargs = None, kwarg_name: str = "_session"):
        super().__init__()
        self.engine: sqlalchemy.engine.Engine = engine
        """
        The :class:`sqlalchemy.engine.Engine` to use.
        """

        self.Session: sqlalchemy.orm.sessionmaker = sqlalchemy.orm.sessionmaker(bind=self.engine)
        """
        The :class:`sqlalchemy.orm.sessionmaker` to use when creating new sessions.
        """

        self.session_kwargs: t.Kwargs = {"future": True, **(session_kwargs or {})}
        """
        Additional kwargs to be passed to the :class:`sqlalchemy.orm.sessionmaker` when instantiating a new Session.
        
        Defaults to ``{"future": True}`` .
        """

        self.kwarg_name: str = kwarg_name
        """
        The name of the kwarg to add.
        
        Defaults to ``"_session"``.
        """

    def __repr__(self):
        return f"<{self.__class__.__qualname__} with engine {self.engine}>"

    @contextlib.asynccontextmanager
    async def kwargs(self, kwargs: t.Kwargs) -> t.Kwargs:
        log.debug(f"{self!r}: Creating session...")
        with self.Session(**self.session_kwargs) as session:
            log.debug(f"{self!r}: Yielding kwargs...")
            yield {
                **kwargs,
                self.kwarg_name: session,
            }
            log.debug(f"{self!r}: Closing session...")
        log.debug(f"{self!r}: Session closed!")


class AsyncSQLAlchemyExtension(base.PDAExtension):
    """
    Extends a :class:`~royalnet.engineer.pda.implementations.base.PDAImplementation` by adding an asyncronous
    :mod:`sqlalchemy` session to conversations through the ``_asession`` kwarg.
    """

    def __init__(self, engine: sea.AsyncEngine, session_kwargs: t.Kwargs = None, kwarg_name: str = "_asession"):
        super().__init__()
        self.engine: sea.AsyncEngine = engine
        """
        The :class:`sqlalchemy.engine.Engine` to use.
        """

        self.AsyncSession: sqlalchemy.orm.sessionmaker = sqlalchemy.orm.sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            class_=sea.AsyncSession,
        )
        """
        The :class:`sqlalchemy.orm.sessionmaker` to use when creating new sessions.
        """

        self.session_kwargs: t.Kwargs = {"future": True, **(session_kwargs or {})}
        """
        Additional kwargs to be passed to the :class:`sqlalchemy.orm.sessionmaker` when instantiating a new Session.
        
        Defaults to ``{"future": True}`` .
        """

        self.kwarg_name: str = kwarg_name
        """
        The name of the kwarg to add.
        
        Defaults to ``"_asession"``.
        """

    def __repr__(self):
        return f"<{self.__class__.__qualname__} with engine {self.engine}>"

    @contextlib.asynccontextmanager
    async def kwargs(self, kwargs: t.Kwargs) -> t.Kwargs:
        log.debug(f"{self!r}: Creating session...")
        async with self.AsyncSession(**self.session_kwargs) as session:
            log.debug(f"{self!r}: Yielding kwargs...")
            yield {
                **kwargs,
                self.kwarg_name: session,
            }
            log.debug(f"{self!r}: Closing session...")
        log.debug(f"{self!r}: Session closed!")


__all__ = (
    "SQLAlchemyExtension",
    "AsyncSQLAlchemyExtension",
)
