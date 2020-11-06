class Updatable:
    """
    A mixin that can be added to a declared class to add update methods, allowing attributes to be set from
    a dict.
    """

    def update(self, **kwargs):
        """Set attributes from the kwargs, ignoring non-existant key/columns."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def set(self, **kwargs):
        """Set attributes from the kwargs, without checking for non-existant key/columns."""
        for key, value in kwargs.items():
            setattr(self, key, value)
