import pytest
from pydantic import BaseModel, Field

from flask_openapi import OpenAPI

app = OpenAPI(__name__)
app.config["TESTING"] = True


class MessageResponse(BaseModel):
    message: str = Field(..., description="The message")
    metadata: dict[str, str] = Field(alias="metadata_")

    model_config = dict(by_alias=False)


@app.post("/body", responses={"200": MessageResponse})
def api_error_json(): ...


@pytest.fixture
def client():
    client = app.test_client()

    return client


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    _json = resp.json
    assert resp.status_code == 200
    assert _json["components"]["schemas"]["MessageResponse"]["properties"].get("metadata") is not None
