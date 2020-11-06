import pydantic_sqlalchemy
import functools


class PyModel:
    """A mixin that can be added to a declared class to generate a Pydantic model from it."""

    @classmethod
    def pydantic(cls):
        return pydantic_sqlalchemy.sqlalchemy_to_pydantic(cls)


__all__ = (
    "PyModel",
)
