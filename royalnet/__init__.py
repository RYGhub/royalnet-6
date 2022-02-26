"""
Royalnet is a collection of many Python modules useful to build chat-like applications.

The modules currently are:

- :mod:`.alchemist`, containing utility extensions to :mod:`sqlalchemy`;
- :mod:`.engineer`, containing a framework for building chat bots;
- :mod:`.lazy`, containing utilities to delay the evaluation of values until they are actually used;
- :mod:`.scrolls`, containing configuration utilities;
- :mod:`.sculptor`, containing common :mod:`pydantic` models for serialization and deserialization of data structures;

To prevent the library from breaking if optional dependencies are not installed, this module does not export any object; submodules should be directly imported instead.

All modules use exceptions based on :exc:`.exc.RoyalnetException`, and may subclass it to provide more detail on the errors.
"""
