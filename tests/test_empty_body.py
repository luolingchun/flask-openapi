import pytest
from pydantic import BaseModel

from flask_openapi import Info, OpenAPI

info = Info(title="book API", version="1.0.0")

app = OpenAPI(__name__, info=info)
app.config["TESTING"] = True


class CreateBookBody(BaseModel):
    pass

    model_config = {
        "extra": "allow",
    }


@pytest.fixture
def client():
    client = app.test_client()

    return client


@app.post("/book")
def create_book(body: CreateBookBody):
    print(body.model_dump())
    return {"code": 0, "message": "ok"}


def test_post(client):
    resp = client.post("/book", json={"aaa": 111, "bbb": 222})
    print(resp.json)
    assert resp.status_code == 200
