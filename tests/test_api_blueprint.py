import pytest
from pydantic import BaseModel, Field

from flask_openapi import APIBlueprint, OpenAPI

app = OpenAPI(__name__)
app.config["TESTING"] = True

api = APIBlueprint("/book", __name__, url_prefix="/api")

try:
    api.register_api(api)
except ValueError as e:
    assert str(e) == "Cannot register a api blueprint on itself"


@pytest.fixture
def client():
    client = app.test_client()

    return client


class BookBody(BaseModel):
    age: int | None = Field(..., ge=2, le=4, description="Age")
    author: str = Field(None, min_length=2, max_length=4, description="Author")


class BookPath(BaseModel):
    id: int = Field(..., description="book id")


@api.get("/book/<id>")
def get_book(path: BookPath):
    assert path.id == 1
    return {"code": 0, "message": "ok"}


@api.post("/book")
def create_book(body: BookBody):
    assert body.age == 3
    return {"code": 0, "message": "ok"}


@api.put("/book/<id>", operation_id="update")
def update_book(path: BookPath, body: BookBody):
    assert path.id == 1
    assert body.age == 3
    return {"code": 0, "message": "ok"}


@api.patch("/book/<id>")
def update_book1(path: BookPath, body: BookBody):
    assert path.id == 1
    assert body.age == 3
    return {"code": 0, "message": "ok"}


@api.delete("/book/<id>")
def delete_book(path: BookPath):
    assert path.id == 1
    return {"code": 0, "message": "ok"}


# register api
app.register_api(api)


def test_get(client):
    resp = client.get("/api/book/1")
    assert resp.status_code == 200


def test_post(client):
    resp = client.post("/api/book", json={"age": 3})
    assert resp.status_code == 200


def test_put(client):
    resp = client.put("/api/book/1", json={"age": 3})
    assert resp.status_code == 200


def test_patch(client):
    resp = client.patch("/api/book/1", json={"age": 3})
    assert resp.status_code == 200


def test_delete(client):
    resp = client.delete("/api/book/1")
    assert resp.status_code == 200


class AuthorBody(BaseModel):
    age: int | None = Field(..., ge=1, le=100, description="Age")


def register_apis():
    _app = OpenAPI(__name__)
    _app.register_api(api, url_prefix="/1.0")


# Invoke twice to ensure that call is idempotent
register_apis()
register_apis()


def test_blueprint_path_and_prefix():
    assert list(api.paths.keys()) == ["/1.0/book/{id}", "/1.0/book"]
