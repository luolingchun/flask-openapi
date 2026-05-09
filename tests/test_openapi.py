from __future__ import annotations

import pytest
from openapi_spec_validator import validate
from pydantic import BaseModel

from flask_openapi import APIBlueprint, OpenAPI, ValidationErrorModel
from tests.config import JWT

servers = [{"url": "https://www.openapis.org/", "description": "openapi"}]
external_docs = {"url": "https://www.openapis.org/", "description": "Something great got better, get excited!"}
tags = [{"name": "book", "description": "book description"}]


class ErrorModel(BaseModel):
    code: int
    message: str


class NewValidationErrorModel(ValidationErrorModel):
    error: ErrorModel | None = None


app = OpenAPI(
    __name__,
    info={"title": "openapi", "version": "2.0"},
    servers=servers,
    external_docs=external_docs,
    validation_error_model=NewValidationErrorModel,
)

api = APIBlueprint("/book", __name__, abp_tags=[{"name": "api name"}], url_prefix="/api")


@pytest.fixture
def client():
    client = app.test_client()

    return client


@app.get(
    "/book1",
    doc_ui=False,
)
def get_book1(): ...


@app.post(
    "/book2",
    summary="Book2",
    description="Book description",
    external_docs=external_docs,
    deprecated=False,
    security=JWT,
    servers=servers,
    tags=tags,
    responses={"422": ErrorModel},
)
def get_book2(): ...


@api.get(
    "/book1",
    doc_ui=False,
)
def get_api_book1(): ...


@api.get(
    "/book2",
    external_docs=external_docs,
    deprecated=False,
    security=JWT,
    servers=servers,
    tags=tags,
    responses={"422": ErrorModel},
)
def get_api_book2(): ...


app.register_api(api)


def test_openapi(client):
    response = client.get("/openapi/openapi.json")
    assert response.status_code == 200
    _json = response.json
    validate(_json)
