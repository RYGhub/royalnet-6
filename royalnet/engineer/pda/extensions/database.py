"""
.. todo:: Document this.
"""

import royalnet.royaltyping as t
import sqlalchemy
import sqlalchemy.orm
import contextlib

from . import base


class SQLAlchemyExtension(base.PDAExtension):
    """
    .. todo:: Document this.
    """

    def __init__(self, engine: sqlalchemy.engine.Engine, session_kwargs: t.Kwargs = None):
        super().__init__()
        self.engine: sqlalchemy.engine.Engine = engine
        self.Session: sqlalchemy.orm.sessionmaker = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.session_kwargs: t.Kwargs = {"future": True, **(session_kwargs or {})}

    @contextlib.asynccontextmanager
    async def kwargs(self, kwargs: dict[str, t.Any]) -> dict[str, t.Any]:
        with self.Session(**self.session_kwargs) as session:
            yield {
                **kwargs,
                "_session": session,
            }


__all__ = (
    "SQLAlchemyExtension",
)
