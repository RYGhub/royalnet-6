from royalnet.typing import *
import os
import json
import re

from .errors import *


class Scroll:
    """A configuration handler that allows getting values from both the environment variables and a config file."""

    key_validator = re.compile(r"^[A-Z.]+$")

    def __init__(self, namespace: str, config: Optional[Dict[str, JSON]] = None):
        self.namespace: str = namespace
        self.config: Optional[Dict[str, JSON]] = config

    @classmethod
    def _validate_key(cls, item: str):
        check = cls.key_validator.match(item)
        if not check:
            raise InvalidFormatError()

    def _get_from_environ(self, item: str) -> JSONScalar:
        """Get a configuration value from the environment variables."""
        key = f"{self.namespace}_{item.replace('.', '_')}"

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

        chain = item.split(".")

        current = self.config

        for element in chain:
            try:
                current = current[element]
            except KeyError:
                raise NotFoundError(f"'{item}' was unreachable: could not find '{element}'")

        return current

    def __getattribute__(self, item: str):
        self._validate_key(item)
        try:
            return self._get_from_environ(item)
        except NotFoundError:
            return self._get_from_config(item)


__all__ = ("Scroll",)
