from royalnet.typing import *
import os
import json
import re
import toml
import json

from .exc import *


class Scroll:
    """A configuration handler that allows getting values from both the environment variables and a config file."""

    key_validator = re.compile(r"^[A-Za-z.]+$")

    loaders = {
        ".json": json.load,
        ".toml": toml.load
    }

    def __init__(self, namespace: str, config: Optional[Dict[str, JSON]] = None):
        self.namespace: str = namespace
        self.config: Optional[Dict[str, JSON]] = config

    @classmethod
    def from_toml(cls, namespace: str, file_path: os.PathLike):
        with open(file_path) as file:
            config = toml.load(file)
        return cls(namespace, config)

    @classmethod
    def from_json(cls, namespace: str, file_path: os.PathLike):
        with open(file_path) as file:
            config = json.load(file)
        return cls(namespace, config)

    @classmethod
    def from_file(cls, namespace: str, file_path: os.PathLike):
        file, ext = os.path.splitext(file_path)
        lext = ext.lower()

        with open(file_path) as file:
            try:
                config = cls.loaders[lext](file)
            except KeyError:
                raise InvalidFileType(f"Invalid extension: {lext}")

        return cls(namespace, config)

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


__all__ = ("Scroll",)
