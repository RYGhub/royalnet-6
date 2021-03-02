"""
Base models are :class:`pydantic.BaseModel` that have specific configuration tailored for certain uses.
"""

import pydantic


class RoyalnetModel(pydantic.BaseModel):
    """
    A model for generic data.
    """

    class Config(pydantic.BaseModel.Config):
        """
        The default :mod:`pydantic` configuration.

        .. seealso:: `Pydantic Configuration <https://pydantic-docs.helpmanual.io/usage/model_config/>`_,
                     :class:`pydantic.BaseModel.Config`
        """
        pass


class OrmModel(RoyalnetModel):
    """
    A model for :mod:`sqlalchemy` table data.
    """

    class Config(RoyalnetModel.Config):
        """
        A configuration which allows for the loading of data from ``__getattr__`` instead of ``__getitem__``.

        .. seealso:: `Pydantic ORM Mode <https://pydantic-docs.helpmanual.io/usage/models/#orm-mode-aka-arbitrary
                     -class-instances>`_
        """
        orm_mode = True


__all__ = (
    "RoyalnetModel",
    "OrmModel",
)
