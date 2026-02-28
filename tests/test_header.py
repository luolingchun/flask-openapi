from enum import Enum

import pytest
from pydantic import BaseModel, Field

from flask_openapi import OpenAPI

app = OpenAPI(__name__)


@pytest.fixture
def client():
    client = app.test_client()

    return client


class TypeEnum(str, Enum):
    A = "A"
    B = "B"


class AuthorModel(BaseModel):
    name: str
    age: int


class BookHeader(BaseModel):
    name: str = Field(
        None,
        description="Name",
        deprecated=True,
        json_schema_extra={
            "example": 1,
            "examples": {"example1": {"value": 1}, "example2": {"value": 2}},
        },
    )
    authors: list[AuthorModel] | None = None
    Hello1: str = Field("what's up", max_length=12, description="sds")
    # required
    hello2: str = Field(..., max_length=12, description="sds")
    api_key: str = Field(..., description="API Key")
    api_type: TypeEnum | None = None
    x_hello: str = Field(..., max_length=12, description="Header with alias to support dash", alias="x-hello")
    null: None = None


class BookHeaderPopulateByName(BookHeader):
    model_config = {"populate_by_name": True}


@app.get("/header")
def get_book(header: BookHeader):
    return header.model_dump(by_alias=True)


@app.get("/header/populate_by_name")
def get_book_populate_by_name(header: BookHeaderPopulateByName):
    return header.model_dump(by_alias=True)


def test_header(client):
    headers = {"Hello1": "111", "hello2": "222", "api_key": "333", "api_type": "A", "x-hello": "444"}
    resp = client.get("/header", headers=headers)
    assert resp.status_code == 200
    assert resp.json == {
        "Hello1": "111",
        "api_key": "333",
        "api_type": "A",
        "authors": None,
        "hello2": "222",
        "name": None,
        "null": None,
        "x-hello": "444",
    }


def test_header_populate_by_name(client):
    headers = {"Hello1": "111", "hello2": "222", "api_key": "333", "api_type": "A", "x-hello": "444"}
    resp = client.get("/header/populate_by_name", headers=headers)
    assert resp.status_code == 200
    assert resp.json == {
        "Hello1": "111",
        "api_key": "333",
        "api_type": "A",
        "authors": None,
        "hello2": "222",
        "name": None,
        "null": None,
        "x-hello": "444",
    }
