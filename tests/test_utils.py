import pytest
from pydantic import BaseModel, Field

from flask_openapi.utils import normalize_name, parse_cookie, parse_header, parse_path, parse_query


def test_normalize_name():
    assert "List-Generic.Response_Detail_" == normalize_name("List-Generic.Response[Detail]")


@pytest.mark.parametrize("parse", [parse_header, parse_cookie, parse_path, parse_query])
def test_parse_parameters_with_json_schema_examples(parse):
    class Model(BaseModel):
        name: str = Field(..., examples=["alice", "bob"])
        age: int = Field(..., json_schema_extra={"examples": {"one": {"value": 1}}})

    parameters, _ = parse(Model)
    params = {p.name: p for p in parameters}

    # a JSON Schema examples list stays in the schema
    assert params["name"].examples is None
    assert params["name"].param_schema.examples == ["alice", "bob"]
    # an OpenAPI map of Example objects is still set on the parameter
    assert params["age"].examples["one"].value == 1
