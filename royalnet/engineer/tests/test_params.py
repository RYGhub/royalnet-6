import pytest
import inspect
import pydantic
import pydantic.fields
import royalnet.engineer as re


@pytest.fixture
async def my_async_function():
    def f(*, big_f: str, _hidden: int) -> str:
        return big_f
    return f


def test_parameter_to_field(my_async_function):
    signature = inspect.signature(my_async_function)
    parameter = signature.parameters["big_f"]
    t, fieldinfo = re.parameter_to_field(parameter)
    assert isinstance(fieldinfo, pydantic.fields.FieldInfo)
    assert fieldinfo.default is ...
    assert fieldinfo.title == parameter.name == "big_f"


def test_signature_to_model(my_async_function):
    Model = re.signature_to_model(my_async_function)
    assert callable(Model)

    model = Model(big_f="banana")
    assert isinstance(model, pydantic.BaseModel)
    assert model.big_f == "banana"
    assert model.dict() == {"big_f": "banana"}

    with pytest.raises(pydantic.ValidationError):
        Model()

    model = Model(big_f="exists", _hidden="no")
    assert isinstance(model, pydantic.BaseModel)
    assert model.big_f == "exists"
    with pytest.raises(AttributeError):
        model._hidden

    with pytest.raises(pydantic.ValidationError):
        Model(big_f=...)
