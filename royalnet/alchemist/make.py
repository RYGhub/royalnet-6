from royalnet.royaltyping import *
import sqlalchemy.orm as o


T = TypeVar('T')


class Makeable:
    """
    A mixin that can be added to a declared class to add the make and unmake methods, that try find an item with
    specific properties and either create it if it doesn't exist or delete it if it exists.
    """

    @classmethod
    def make(cls: Type[T], session: o.session.Session, **kwargs) -> T:
        """
        Find the item with the specified name, or create it if it doesn't exist.

        :param session: The session to be used in the query and creation.
        :param kwargs: Arguments to use in the :meth:`~sqlalchemy.orm.query.Query.filter_by` clause and in the item
                       constructor.
        :return: The retrieved or created item.
        """
        # Find the item
        item = session.query(cls).filter_by(**kwargs).one_or_none()
        # Create the item
        if item is None:
            item = cls(**kwargs)
            session.add(item)
        # Return the item
        return item

    @classmethod
    def unmake(cls: Type[T], session: o.session.Session, **kwargs) -> None:
        """
        Find the item with the specified name, and delete it if it exists.

        :param session: The session to be used in the query and creation.
        :param kwargs: Arguments to use in the :meth:`~sqlalchemy.orm.query.Query.filter_by` clause and in the item
                       constructor.
        """
        # Find the item
        item = session.query(cls).filter_by(**kwargs).one_or_none()
        # Delete the item
        if item is not None:
            session.delete(item)


__all__ = (
    "Makeable",
)
