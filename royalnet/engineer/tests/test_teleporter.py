import pytest
import inspect
import pydantic
import pydantic.fields
import royalnet.engineer.teleporter as tp


@pytest.fixture
def my_function():
    # noinspection PyUnusedLocal
    def f(*, big_f: str, _hidden: int) -> int:
        return _hidden
    return f


def test_parameter_to_field(my_function):
    signature = inspect.signature(my_function)
    parameter = signature.parameters["big_f"]
    t, fieldinfo = tp.parameter_to_field(parameter)
    assert isinstance(fieldinfo, pydantic.fields.FieldInfo)
    assert fieldinfo.default is ...
    assert fieldinfo.title == parameter.name == "big_f"


def test_signature_to_model(my_function):
    # noinspection PyPep8Naming
    InputModel, OutputModel = tp.signature_to_model(my_function)
    assert callable(InputModel)

    model = InputModel(big_f="banana")
    assert isinstance(model, pydantic.BaseModel)
    assert model.big_f == "banana"
    assert model.dict() == {"big_f": "banana"}

    with pytest.raises(pydantic.ValidationError):
        InputModel()

    model = InputModel(big_f="exists", _hidden="no")
    assert isinstance(model, pydantic.BaseModel)
    assert model.big_f == "exists"
    with pytest.raises(AttributeError):
        _ = model._hidden

    with pytest.raises(pydantic.ValidationError):
        InputModel(big_f=...)

    model = OutputModel(__root__=42)
    assert isinstance(model, pydantic.BaseModel)
    assert model.__root__ == 42
    assert model.dict() == {"__root__": 42}

    with pytest.raises(pydantic.ValidationError):
        OutputModel()

    with pytest.raises(pydantic.ValidationError):
        OutputModel(__root__="sì")


# noinspection PyTypeChecker
class TestTeleporter:
    def test_standard_function(self):
        @tp.teleport()
        def standard_function(a: int, b: int, _return_str: bool = False) -> int:
            if _return_str:
                return "You asked me this."
            return a+b

        assert standard_function(a=1, b=2) == 3
        assert standard_function(a="1", b="2") == 3
        assert standard_function(a="1", b=2) == 3

        with pytest.raises(pydantic.ValidationError):
            _ = standard_function(a="sì", b="no")

        with pytest.raises(pydantic.ValidationError):
            _ = standard_function(a=1, b="no")

        with pytest.raises(pydantic.ValidationError):
            _ = standard_function(a="sì", b=2)

        with pytest.raises(pydantic.ValidationError):
            _ = standard_function(a="sì")

        with pytest.raises(pydantic.ValidationError):
            _ = standard_function(b="sì")

        with pytest.raises(pydantic.ValidationError):
            _ = standard_function(a=1, b=2, _return_str=True)

        with pytest.raises(TypeError):
            _ = standard_function(1, 2)

    @pytest.mark.asyncio
    async def test_async_function(self):
        @tp.teleport(is_async=True)
        async def async_function(a: int, b: int, _return_str: bool = False) -> int:
            if _return_str:
                return "You asked me this."
            return a+b

        assert await async_function(a=1, b=2) == 3
        assert await async_function(a="1", b="2") == 3
        assert await async_function(a="1", b=2) == 3

        with pytest.raises(pydantic.ValidationError):
            _ = await async_function(a="sì", b="no")

        with pytest.raises(pydantic.ValidationError):
            _ = await async_function(a=1, b="no")

        with pytest.raises(pydantic.ValidationError):
            _ = await async_function(a="sì", b=2)

        with pytest.raises(pydantic.ValidationError):
            _ = await async_function(a="sì")

        with pytest.raises(pydantic.ValidationError):
            _ = await async_function(b="sì")

        with pytest.raises(pydantic.ValidationError):
            _ = await async_function(a=1, b=2, _return_str=True)

        with pytest.raises(TypeError):
            _ = await async_function(1, 2)

    def test_only_input(self):
        @tp.teleport(validate_output=False)
        def standard_function(a: int, b: int, _return_str: bool = False) -> int:
            if _return_str:
                return "You asked me this."
            return a+b

        assert standard_function(a=1, b=2) == 3
        assert standard_function(a="1", b="2") == 3
        assert standard_function(a="1", b=2) == 3

        with pytest.raises(pydantic.ValidationError):
            _ = standard_function(a="sì", b="no")

        with pytest.raises(pydantic.ValidationError):
            _ = standard_function(a=1, b="no")

        with pytest.raises(pydantic.ValidationError):
            _ = standard_function(a="sì", b=2)

        with pytest.raises(pydantic.ValidationError):
            _ = standard_function(a="sì")

        with pytest.raises(pydantic.ValidationError):
            _ = standard_function(b="sì")

        assert standard_function(a=1, b=2, _return_str=True) == "You asked me this."

        with pytest.raises(TypeError):
            _ = standard_function(1, 2)

    def test_only_output(self):
        @tp.teleport(validate_input=False)
        def standard_function(a: int, b: int, _return_str: bool = False) -> int:
            if _return_str:
                return "You asked me this."
            return a+b

        assert standard_function(a=1, b=2) == 3
        assert standard_function(a="1", b="2") == 12

        with pytest.raises(TypeError):
            assert standard_function(a="1", b=2) == 3

        with pytest.raises(pydantic.ValidationError):
            assert standard_function(a="sì", b="no") == "sìno"

        with pytest.raises(TypeError):
            _ = standard_function(a=1, b="no")

        with pytest.raises(TypeError):
            _ = standard_function(a="sì", b=2)

        with pytest.raises(TypeError):
            _ = standard_function(a="sì")

        with pytest.raises(TypeError):
            _ = standard_function(b="sì")

        with pytest.raises(pydantic.ValidationError):
            _ = standard_function(a=1, b=2, _return_str=True)

        with pytest.raises(TypeError):
            _ = standard_function(1, 2)
