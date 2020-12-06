"""
This module defines a class that can be used to easily load configuration from a :mod:`json` or :mod:`toml` file and
from :data:`os.environ`.
"""

from __future__ import annotations
from royalnet.royaltyping import *
import os
import re
import toml
import json

from .exc import *


T = TypeVar("T")


class Scroll:
    """
    A configuration handler that allows getting values from both the environment variables and a config file.
    """

    key_validator = re.compile(r"^[A-Za-z.]+$")
    """
    A regex used to validate config keys.
    """

    def __init__(self, namespace: str, config: Optional[Dict[str, JSON]] = None):
        self.namespace: str = namespace
        self.config: Optional[Dict[str, JSON]] = config

    @classmethod
    def from_toml(cls, namespace: str, file_path: os.PathLike) -> Scroll:
        """
        Create a new :class:`.Scroll` from a :mod:`toml` file.

        :param namespace: A string prefixed to the environment variable keys to disambiguate between multiple scroll
                          objects.
        :param file_path: The path of the :mod:`toml` file to load.
        :return: The created :class:`.Scroll` object.
        """
        with open(file_path) as file:
            config = toml.load(file)
        return cls(namespace, config)

    @classmethod
    def from_json(cls, namespace: str, file_path: os.PathLike) -> Scroll:
        """
        Create a new :class:`.Scroll` from a :mod:`json` file.

        :param namespace: A string prefixed to the environment variable keys to disambiguate between multiple scroll
                          objects.
        :param file_path: The path of the :mod:`json` file to load.
        :return: The created :class:`.Scroll` object.
        """
        with open(file_path) as file:
            config = json.load(file)
        return cls(namespace, config)

    @classmethod
    def from_file(cls, namespace: str, file_path: os.PathLike, require_file: bool = False) -> Scroll:
        """
        Try to guess the type of the config file and create a new :class:`.Scroll` from it.

        :param namespace: A string prefixed to the environment variable keys to disambiguate between multiple scroll
                          objects.
        :param file_path: The path of the file to load.
        :param require_file: Require the file to exist for the :class:`.Scroll` to be created.
        :raise .exc.InvalidFileType: If the file format isn't supported.
        :raise .exc.MissingConfigFile: If ``require_file`` is set to :data:`True` and the config file does not exist.
        :return: The created :class:`.Scroll` object.
        """
        if require_file and not os.path.exists(file_path):
            raise MissingConfigFileError(f"No config file exists at path {file_path}, and require_file is set to True.")

        _, ext = os.path.splitext(file_path)
        lext = ext.lower()

        try:
            return cls.loaders[lext](namespace=namespace, file_path=file_path)
        except KeyError:
            raise InvalidFileType(f"Invalid extension: {lext}")
        except FileNotFoundError:
            return cls(namespace=namespace)

    @classmethod
    def _validate_key(cls, item: str):
        check = cls.key_validator.match(item)
        if not check:
            raise InvalidFormatError()

    def _get_from_environ(self, item: str) -> JSONScalar:
        """Get a configuration value from the environment variables."""
        key = f"{self.namespace}_{item.replace('.', '_')}".upper()

        try:
            j = os.environ[key]
        except KeyError:
            raise NotFoundError(f"'{key}' was not found in the environment variables.")

        try:
            value = json.loads(j)
        except json.JSONDecodeError:
            raise ParseError(f"'{key}' contains invalid JSON: {j}")

        return value

    def _get_from_config(self, item: str) -> JSONScalar:
        """Get a configuration value from the configuration file."""
        if self.config is None:
            raise NotFoundError("No config file has been loaded.")

        chain = item.lower().split(".")

        current = self.config

        for element in chain:
            try:
                current = current[element]
            except KeyError:
                raise NotFoundError(f"'{item}' was unreachable: could not find '{element}'")

        return current

    def __getitem__(self, item: str):
        self._validate_key(item)
        try:
            return self._get_from_environ(item)
        except NotFoundError:
            return self._get_from_config(item)

    def get(self, item: str, default: T) -> Union[JSONScalar, T]:
        try:
            return self[item]
        except NotFoundError:
            return default


Scroll.loaders = {
    ".json": Scroll.from_json,
    ".toml": Scroll.from_toml,
}
"""
An extension to deserialization function map.
"""


__all__ = ("Scroll",)
