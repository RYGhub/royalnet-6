class ColRepr:
    """
    A mixin that can be added to a declared class to display all columns of the table with their values in the
    ``__repr__``.
    """

    def __repr__(self):
        columns = [c.name for c in self.__class__.__table__.columns]
        args = [f"{c}={repr(self.__getattribute__(c))}" for c in columns]
        return f"{self.__class__.__qualname__}({', '.join(args)})"


__all__ = (
    "ColRepr",
)
