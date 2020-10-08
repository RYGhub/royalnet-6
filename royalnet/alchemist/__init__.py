from royalnet.typing import *
import sqlalchemy as sa
import sqlalchemy.orm as saorm


__all__ = (
    "Alchemist",
)


class Alchemist:
    """The Alchemist module connects to a relational database with SQLAlchemy."""

    def __init__(self,
                 engine_args: Iterable[Any],
                 engine_kwargs: Mapping[str, Any]):
        self.engine: sa.engine.Engine = sa.create_engine(*engine_args, **engine_kwargs)
        self.Session: Union[saorm.sessionmaker, Type[saorm.Session]] = saorm.sessionmaker(bind=self.engine)

    def add_metadata(self, metadata: sa.MetaData):
        """Bind a MetaData object to the engine, and create all tables linked with it."""
        metadata.bind = self.engine
        metadata.create_all()
