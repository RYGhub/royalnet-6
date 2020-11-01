from ..typing import *
import sqlalchemy


def ieq(one, two):
    """
    Create a case-insensitive equality filter for SQLAlchemy. ::

        lower(one) == lower(two)


    """
    return sqlalchemy.func.lower(one) == sqlalchemy.func.lower(two)


def ineq(one, two):
    """
    Create a case-insensitive inequality filter for SQLAlchemy. ::

        lower(one) != lower(two)


    """
    return sqlalchemy.func.lower(one) != sqlalchemy.func.lower(two)


__all__ = (
    "ieq",
    "ineq",
)
