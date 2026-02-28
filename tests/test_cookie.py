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


class BookCookie(BaseModel):
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
    token: str | None = None
    token_type: TypeEnum | None = None


@app.post("/cookie")
def post_cookie(cookie: BookCookie):
    return cookie.model_dump(by_alias=True)


def test_cookie(client):
    client.set_cookie("token", "xxx")
    client.set_cookie("token_type", "A")
    r = client.post("/cookie")
    assert r.status_code == 200
    assert r.json == {"authors": None, "name": None, "token": "xxx", "token_type": "A"}
