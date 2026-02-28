import pytest
from pydantic import BaseModel

from flask_openapi import OpenAPI

app = OpenAPI(__name__)
app.config["TESTING"] = True


@pytest.fixture
def client():
    client = app.test_client()

    return client


class AuthorModel(BaseModel):
    name: str
    age: int


class BookModel(BaseModel):
    name: str
    authors: list[AuthorModel] | None = None
    files: list[str]


@app.post("/book")
def create_book(body: BookModel):
    return body.model_dump()


def test_post(client):
    data = {"name": "test", "files": ["file1", "file2"]}
    response = client.post("/book", json=data)
    assert response.status_code == 200
    assert response.json == {"authors": None, "files": ["file1", "file2"], "name": "test"}


def test_post_with_error_json(client):
    error_json = '{"aaa:111}'.encode("utf8")
    response = client.post("/book", data=error_json)
    assert response.status_code == 422


def test_str_body(client):
    resp = client.post("/book", json='{"authors":null,"files":["file1","file2"],"name":"test"}')
    assert resp.status_code == 200
