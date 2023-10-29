import pytest

from noneapi import validations


def test_validations_simple_types():
    def test_simple(x: int, y: int):
        return x + y

    assert not validations.validate_or_ignore(test_simple, x=1, y=2)

    with pytest.raises(ValueError):
        assert validations.validate_or_ignore(test_simple, x=1, y="2")


def test_validations_complex_types():


    def test_dict(d: dict[str, int]):
        return d

    assert not validations.validate_or_ignore(test_dict, d={"x": 1, "y": 2})
    assert not validations.validate_or_ignore(test_dict, d={"x": 1, "y": "2"})


def test_validation_pydantic_types():
    from pydantic import BaseModel

    class TestModel(BaseModel):
        x: int
        y: int

    def test_pydantic(model: TestModel):
        return model

    assert not validations.validate_or_ignore(test_pydantic, model={"x": 1, "y": 2})

    with pytest.raises(ValueError):
        assert validations.validate_or_ignore(test_pydantic, model={"x": 1, "y": "qwe"})