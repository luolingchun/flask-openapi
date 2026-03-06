import pytest
from pydantic import BaseModel

from flask_openapi import APIBlueprint, OpenAPI, RequestBody
from flask_openapi.utils import get_model_schema

app = OpenAPI(__name__)
api = APIBlueprint("book", __name__, url_prefix="/api")


@pytest.fixture
def client():
    client = app.test_client()

    return client


class JsonModel(BaseModel):
    name: str
    age: int


request_body_json = {
    "description": "The json request body",
    "content": {"application/custom+json": {"schema": get_model_schema(JsonModel)}},
}

request_body = RequestBody(
    description="The multi request body",
    content={
        "text/plain": {"schema": {"type": "string"}},
        "text/html": {"schema": {"type": "string"}},
        "image/png": {"schema": {"type": "string", "format": "binary"}},
    },
)


@app.post("/json", request_body=request_body_json)
def post_json(body: JsonModel):
    print(body.model_json_schema())
    return {"message": "Hello World"}


@app.post("/text", request_body=request_body)
def post_csv():
    return {"message": "Hello World"}


@api.post("/json", request_body=request_body_json)
def post_api_json():
    return {"message": "Hello World1"}


@api.post("/text", request_body=request_body)
def post_api_csv():
    return {"message": "Hello World"}


app.register_api(api)


def test_get_api_book(client):
    response = client.get("/openapi/openapi.json")
    assert response.status_code == 200
    data = response.json
    assert list(data["paths"]["/json"]["post"]["requestBody"]["content"].keys()) == ["application/custom+json"]
    assert set(data["paths"]["/text"]["post"]["requestBody"]["content"].keys()) == {
        "text/plain",
        "text/html",
        "image/png",
    }


def test(client):
    assert client.post("/json", json={"name": "bob", "age": 3}).status_code == 200
    assert client.post("/text").status_code == 200
    assert client.post("/api/json", json={"name": "bob", "age": 3}).status_code == 200
    assert client.post("/api/text").status_code == 200
