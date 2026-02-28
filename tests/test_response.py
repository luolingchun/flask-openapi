from http import HTTPStatus

import pytest
from pydantic import BaseModel

from flask_openapi import APIBlueprint, OpenAPI, Response

app = OpenAPI(__name__, responses={200: Response(description="OK")})
app.config["TESTING"] = True
api = APIBlueprint("/api", __name__, url_prefix="/api", abp_responses={200: Response(description="API OK")})


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


@app.post("/book1")
def response1(body: BookModel):
    return body.model_json_schema()


@app.post("/book2", responses={HTTPStatus.OK: BookModel})
def response2(body: BookModel):
    return body.model_json_schema()


@app.post(
    "/book3",
    responses={
        "200": {
            "description": "Custom OK",
            "content": {"application/custom+json": {"schema": BookModel.model_json_schema()}},
        },
        "204": None,
    },
)
def response3(body: BookModel):
    return body.model_json_schema()


@api.post("/book4")
def response4(body: BookModel):
    return body.model_json_schema()


@api.post("/book5", responses={HTTPStatus.OK: BookModel})
def response5(body: BookModel):
    return body.model_json_schema()


@api.post(
    "/book6",
    responses={
        "200": {
            "description": "API OK",
            "content": {"application/custom+json": {"schema": BookModel.model_json_schema()}},
        }
    },
)
def response6(body: BookModel):
    return body.model_json_schema()


app.register_api(api)


def test_response(client):
    response = client.get("/openapi/openapi.json")
    _json = response.json
    assert _json["paths"]["/book1"]["post"]["responses"]["200"]["description"] == "OK"
    assert _json["paths"]["/book2"]["post"]["responses"]["200"]["content"]["application/json"] is not None
    assert _json["paths"]["/book3"]["post"]["responses"]["200"]["content"]["application/custom+json"] is not None
    assert _json["paths"]["/api/book4"]["post"]["responses"]["200"]["description"] == "API OK"
    assert _json["paths"]["/api/book5"]["post"]["responses"]["200"]["content"]["application/json"] is not None
    assert _json["paths"]["/api/book6"]["post"]["responses"]["200"]["content"]["application/custom+json"] is not None


def test(client):
    assert client.post("/book1", json={"name": "bob", "age": 3}).status_code == 200
    assert client.post("/book2", json={"name": "bob", "age": 3}).status_code == 200
    assert client.post("/book3", json={"name": "bob", "age": 3}).status_code == 200
    assert client.post("/api/book4", json={"name": "bob", "age": 3}).status_code == 200
    assert client.post("/api/book5", json={"name": "bob", "age": 3}).status_code == 200
    assert client.post("/api/book6", json={"name": "bob", "age": 3}).status_code == 200
