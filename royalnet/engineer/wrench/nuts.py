from royalnet.royaltyping import *
import abc
from .. import exc, blueprints


class Nut(metaclass=abc.ABCMeta):
    """
    A wrapper to easily pass parameters to filter functions for :class:`royalnet.engineer.wrench.WrenchNode`.
    """

    @abc.abstractmethod
    async def filter(self, obj: Any) -> Any:
        """
        The function applied to all objects transiting through the tree:

        - If the function **returns**, its return value will be passed to the next node in the tree;
        - If the function **raises**, the error is propagated downwards.

        A special exception is available for discarding objects: :exc:`.exc.Discard`.
        If raised, :meth:`royalnet.engineer.wrench.Wrench.get` will silently ignore the object.
        """
        raise NotImplementedError()

    def __call__(self, obj: Any) -> Awaitable[Any]:
        """
        Allow instances to be directly called, emulating coroutine functions.
        """
        return self.filter(obj)


class Pass(Nut):
    """
    **Return** each received object as it is.
    """

    async def filter(self, obj: Any) -> Any:
        return obj


class Discard(Nut):
    """
    **Discard** each received object.
    """

    async def filter(self, obj: Any) -> Any:
        raise exc.Discard(obj, "Discard filter discards everything")


class Check(Nut, metaclass=abc.ABCMeta):
    """
    Check a condition on the received objects:

    - If the check returns :data:`True`, the object is **returned**;
    - If the check returns :data:`False`, the object is **discarded**;
    - If an error is raised, it is **propagated**.
    """

    def __init__(self, *, invert: bool = False):
        self.invert: bool = invert
        """
        If set to :data:`True`, this Nut will invert its results:
        
        - If the check returns :data:`True`, the object is **discarded**;
        - If the check returns :data:`False`, the object is **returned**;
        - If an error is raised, it is **propagated**.
        """

    def __invert__(self):
        return self.__class__(invert=not self.invert)

    @abc.abstractmethod
    async def check(self, obj: Any) -> bool:
        """
        The condition to check.

        :param obj: The object passing through the tree.
        :return: Whether the check was successful or not.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def error(self, obj: Any) -> str:
        """
        The error message to attach as :attr:`.exc.Discard.message` if the object is discarded.

        :param obj: The object passing through the tree.
        :return: The error message.
        """
        raise NotImplementedError()

    async def filter(self, obj: Any) -> Any:
        if await self.check(obj) ^ self.invert:
            return obj
        else:
            raise exc.Discard(obj=obj, message=self.error(obj))


class Type(Check):
    """
    Check the type of an object:
    
    - If the object **is** of the specified type, it is **returned**;
    - If the object **isn't** of the specified type, it is **discarded**;
    """

    def __init__(self, t: Type, **kwargs):
        super().__init__(**kwargs)
        self.t: Type = t

    async def check(self, obj: Any) -> bool:
        return isinstance(obj, self.t)

    def error(self, obj: Any) -> str:
        return f"Not instance of type {self.t}"


class StartsWith(Check):
    """
    Check if an object :func:`startswith` a certain prefix.
    """

    def __init__(self, prefix: str, **kwargs):
        super().__init__(**kwargs)
        self.prefix: str = prefix

    async def check(self, obj: Any) -> bool:
        return obj.startswith(self.prefix)

    def error(self, obj: Any) -> str:
        return f"Didn't start with {self.prefix}"


class EndsWith(Check):
    """
    Check if an object :func:`endswith` a certain suffix.
    """

    def __init__(self, suffix: str, **kwargs):
        super().__init__(**kwargs)
        self.suffix: str = suffix

    async def check(self, obj: Any) -> bool:
        return obj.startswith(self.suffix)

    def error(self, obj: Any) -> str:
        return f"Didn't end with {self.suffix}"


class Choice(Check):
    """
    Check if an object is among the accepted list.
    """

    def __init__(self, *accepted, **kwargs):
        super().__init__(**kwargs)
        self.accepted: Collection = accepted
        """
        A collection of elements which can be chosen.
        """

    async def check(self, obj: Any) -> bool:
        return obj in self.accepted

    def error(self, obj: Any) -> str:
        return f"Not a valid choice"


class RegexCheck(Check):
    """
    Check if an object matches a regex pattern.
    """

    def __init__(self, pattern: Pattern, **kwargs):
        super().__init__(**kwargs)
        self.pattern: Pattern = pattern
        """
        The pattern that should be matched.
        """

    async def check(self, obj: Any) -> bool:
        return bool(self.pattern.match(obj))

    def error(self, obj: Any) -> str:
        return f"Didn't match pattern {self.pattern}"


class RegexMatch(Nut):
    """
    Apply a regex over an object:

    - If it matches, **return** the :class:`re.Match` object;
    - If it doesn't match, **discard** the object.
    """

    def __init__(self, pattern: Pattern, **kwargs):
        super().__init__(**kwargs)
        self.pattern: Pattern = pattern
        """
        The pattern that should be matched.
        """

    async def filter(self, obj: Any) -> Any:
        if match := self.pattern.match(obj):
            return match
        else:
            raise exc.Discard(obj, f"Didn't match pattern {obj}")


class RegexReplace(Nut):
    """
    Apply a regex over an object:

    - If it matches, replace the match(es) with :attr:`.replacement` and **return** the result.
    - If it doesn't match, **return** the object as it is.
    """

    def __init__(self, pattern: Pattern, replacement: Union[str, bytes]):
        self.pattern: Pattern = pattern
        """
        The pattern that should be matched.
        """

        self.replacement: Union[str, bytes] = replacement
        """
        The substitution string for the object.
        """

    async def filter(self, obj: Any) -> Any:
        return self.pattern.sub(self.replacement, obj)


class Blueprint(Type):
    """
    Check if an object is a :class:`.blueprint.Blueprint`.
    """

    def __init__(self, **kwargs):
        super().__init__(t=blueprints.Blueprint, **kwargs)


class Message(Type):
    """
    Check if an object is a :class:`.blueprint.Message`.
    """

    def __init__(self, **kwargs):
        super().__init__(t=blueprints.Message, **kwargs)


class BlueprintRequires(Nut):
    """
    Test a :class:`.blueprints.Blueprint`'s fields by using the ``.requires()`` method:

    - If the :class:`.blueprints.Blueprint` has the required fields, **return** it;
    - If the :class:`.blueprints.Blueprint` is missing data in one or more fields (:exc:`.exc.NotAvailableError`),
      **discard** the object;
    - If the :class:`.blueprints.Blueprint` does not support one or more fields (:exc:`.exc.NeverAvailableError`),
      **propagate** :exc:`.exc.NotAvailableError` downwards.

    This behaviour can be changed with :attr:`.propagate_not_available` and :attr:`.propagate_never_available`.

    .. seealso:: :meth:`.blueprints.Blueprint.requires`
    """

    def __init__(self, *fields: str,
                 propagate_not_available: bool = False,
                 propagate_never_available: bool = True):
        self.fields: Collection[str] = fields
        """
        The names of the required fields.
        """

        self.propagate_not_available: bool = propagate_not_available
        """        
        - If :data:`True`, propagate :exc:`.exc.NotAvailableError` downwards.
        - If :data:`False`, discard objects raising :exc:`.exc.NotAvailableError`.
        """

        self.propagate_never_available: bool = propagate_never_available
        """        
        - If :data:`True`, propagate :exc:`.exc.NeverAvailableError` downwards.
        - If :data:`False`, discard objects raising :exc:`.exc.NeverAvailableError`.
        """

    async def filter(self, obj: Any) -> Any:
        try:
            obj.requires(*self.fields)
        except exc.NotAvailableError:
            if self.propagate_not_available:
                raise
            raise exc.Discard(obj, "At least one field is not available")
        except exc.NeverAvailableError:
            if self.propagate_never_available:
                raise
            raise exc.Discard(obj, "At least one field is never available")
        return obj


class BlueprintField(Nut):
    """
    Replace a :class:`.blueprints.Blueprint` with one of its fields.

    - If the :class:`.blueprints.Blueprint` has the required field, **return** its value;
    - If the :class:`.blueprints.Blueprint` is missing data in the field (:exc:`.exc.NotAvailableError`),
      **discard** the object;
    - If the :class:`.blueprints.Blueprint` does not support the field , **propagate**
      :exc:`.exc.NotAvailableError` downwards.

    This behaviour can be changed with :attr:`.propagate_not_available` and :attr:`.propagate_never_available`.

    .. seealso:: :meth:`.blueprints.Blueprint.requires`
    """

    def __init__(self, field: str,
                 propagate_not_available: bool = False,
                 propagate_never_available: bool = True):
        self.field: str = field
        """
        The name of the field.
        """

        self.propagate_not_available: bool = propagate_not_available
        """        
        - If :data:`True`, propagate :exc:`.exc.NotAvailableError` downwards.
        - If :data:`False`, discard objects raising :exc:`.exc.NotAvailableError`.
        """

        self.propagate_never_available: bool = propagate_never_available
        """        
        - If :data:`True`, propagate :exc:`.exc.NeverAvailableError` downwards.
        - If :data:`False`, discard objects raising :exc:`.exc.NeverAvailableError`.
        """

    async def filter(self, obj: Any) -> Any:
        try:
            return obj.__getattribute__(self.field)()
        except exc.NotAvailableError:
            if self.propagate_not_available:
                raise
            raise exc.Discard(obj, f"The field {self.field} has no data available")
        except exc.NeverAvailableError:
            if self.propagate_never_available:
                raise
            raise exc.Discard(obj, f"The field {self.field} never has data available")


__all__ = (
    "Nut",
    "Pass",
    "Check",
    "Type",
    "StartsWith",
    "EndsWith",
    "Choice",
    "RegexCheck",
    "RegexMatch",
    "RegexReplace",
    "Blueprint",
    "Message",
    "BlueprintRequires",
    "BlueprintField",
)
