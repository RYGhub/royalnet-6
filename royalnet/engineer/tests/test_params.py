import pytest
import inspect
import pydantic
import pydantic.fields
import royalnet.engineer as re


@pytest.fixture
def a_random_function():
    def f(big_f: str, _hidden: int) -> str:
        return big_f
    return f


def test_parameter_to_field(a_random_function):
    signature = inspect.signature(a_random_function)
    parameter = signature.parameters["big_f"]
    fieldinfo = re.parameter_to_field(parameter)
    assert isinstance(fieldinfo, pydantic.fields.FieldInfo)
    assert fieldinfo.default == parameter.default == str
    assert fieldinfo.title == parameter.name == "big_f"


def test_signature_to_model(a_random_function):
    Model = re.signature_to_model(a_random_function)
    assert callable(Model)

    model = Model(big_f="banana")
    assert isinstance(model, pydantic.BaseModel)
    assert model.big_f == "banana"
    assert model.dict() == {"big_f": "banana"}

    with pytest.raises(pydantic.ValidationError):
        Model()

    with pytest.raises(pydantic.ValidationError):
        Model(big_f="exists", _hidden="no")

    with pytest.raises(pydantic.ValidationError):
        Model(big_f=1)
