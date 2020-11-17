import sqlalchemy


def ieq(one, two):
    """
    Create a case-insensitive equality filter to be used in :meth:`sqlalchemy.orm.query.Query.filter`.

    Equal to: ::

        lower(one) == lower(two)

    """
    return sqlalchemy.func.lower(one) == sqlalchemy.func.lower(two)


def ineq(one, two):
    """
    Create a case-insensitive inequality filter to be used in :meth:`sqlalchemy.orm.query.Query.filter`.

    Equal to: ::

        lower(one) != lower(two)

    """
    return sqlalchemy.func.lower(one) != sqlalchemy.func.lower(two)


__all__ = (
    "ieq",
    "ineq",
)
