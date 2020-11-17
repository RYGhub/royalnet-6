class Updatable:
    """
    A mixin that can be added to a declared class to add update methods, allowing attributes to be set from
    a :class:`dict`.
    """

    def update(self, **kwargs):
        """Set attributes from the ``kwargs``, ignoring non-existant key/columns."""
        for key, value in kwargs.items():
            if value is DoNotUpdate:
                continue
            if hasattr(self, key):
                setattr(self, key, value)

    def set(self, **kwargs):
        """Set attributes from the ``kwargs``, without checking for non-existant key/columns."""
        for key, value in kwargs.items():
            if value is DoNotUpdate:
                continue
            setattr(self, key, value)


class DoNotUpdateType:
    """
    A type, similar to :data:`None`, used to mark fields that should be skipped in update and set operations.
    """
    __slots__ = ()


DoNotUpdate = DoNotUpdateType()
"""The constant instance of the DoNotUpdateType."""


__all__ = (
    "Updatable",
    "DoNotUpdateType",
    "DoNotUpdate",
)
