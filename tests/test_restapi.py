from __future__ import annotations

import pytest
from pydantic import BaseModel

from flask_openapi import OpenAPI

app = OpenAPI(__name__)
app.config["TESTING"] = True


@pytest.fixture
def client():
    client = app.test_client()

    return client


class IdModel(BaseModel):
    id: int


class BookModel(BaseModel):
    name: str
    age: int


@app.get("/book")
def get_book(query: BookModel):
    return query.model_dump()


@app.post("/book")
def create_book(body: BookModel):
    return body.model_dump()


@app.put("/book/<id>")
def update_book(path: IdModel, body: BookModel):
    return {"id": path.id, "name": body.name, "age": body.age}


@app.patch("/book/<id>")
def patch_book(path: IdModel, body: BookModel):
    return {"id": path.id, "name": body.name, "age": body.age}


@app.delete("/book/<id>")
def delete_book(path: IdModel):
    return {"id": path.id}


def test_get(client):
    response = client.get("/book?name=s&age=3")
    assert response.status_code == 200


def test_post(client):
    data = {"name": "test", "age": 1}
    response = client.post("/book", json=data)
    assert response.status_code == 200
    assert response.json == data


def test_put(client):
    data = {"name": "test", "age": 1}
    response = client.put("/book/1", json=data)
    assert response.status_code == 200


def test_patch(client):
    data = {"name": "test", "age": 1}
    response = client.patch("/book/1", json=data)
    assert response.status_code == 200


def test_delete(client):
    response = client.delete("/book/1")
    assert response.status_code == 200
