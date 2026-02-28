import pytest
from pydantic import BaseModel, Field

from flask_openapi import APIView, OpenAPI
from tests.config import JWT

app = OpenAPI(__name__)
app.config["TESTING"] = True

api_view = APIView(url_prefix="/api")

servers = [{"url": "https://www.openapis.org/", "description": "openapi"}]
external_docs = {"url": "https://www.openapis.org/", "description": "Something great got better, get excited!"}
tags = [{"name": "book", "description": "book description"}]


class ErrorModel(BaseModel):
    code: int
    message: str


class BookPath(BaseModel):
    id: int = Field(..., description="book ID")


class BookQuery(BaseModel):
    age: int | None = Field(None, description="Age")


class BookBody(BaseModel):
    age: int | None = Field(..., ge=2, le=4, description="Age")
    author: str = Field(None, min_length=2, max_length=4, description="Author")


@api_view.route("/book")
class BookListAPIView:
    @api_view.doc(
        summary="get book list",
        description="Book description",
        external_docs=external_docs,
        operation_id="get_book_list",
        deprecated=False,
        security=JWT,
        servers=servers,
        tags=tags,
        responses={"422": ErrorModel},
    )
    def get(self, query: BookQuery):
        return query.model_dump_json()

    @api_view.doc(summary="create book")
    def post(self, body: BookBody):
        return body.model_dump_json()


@api_view.route("/book/<id>")
class BookAPIView:
    @api_view.doc(summary="get book")
    def get(self, path: BookPath):
        return path.model_dump()

    @api_view.doc(summary="update book")
    def put(self, path: BookPath):
        return path.model_dump()

    @api_view.doc(summary="delete book")
    def delete(self, path: BookPath):
        return path.model_dump()


app.register_api_view(api_view)


@pytest.fixture
def client():
    client = app.test_client()

    return client


def test_get_list(client):
    resp = client.get("/api/book")
    assert resp.status_code == 200


def test_post(client):
    resp = client.post("/api/book", json={"age": 3})
    assert resp.status_code == 200


def test_put(client):
    resp = client.put("/api/book/1", json={"age": 3})
    assert resp.status_code == 200


def test_get(client):
    resp = client.get("/api/book/1")
    assert resp.status_code == 200


def test_delete(client):
    resp = client.delete("/api/book/1")
    assert resp.status_code == 200


def register_api_view():
    _app = OpenAPI(__name__)
    _app.register_api_view(api_view, url_prefix="/api/1.0")


def test_register_api_view():
    # Invoke twice to ensure that call is idempotent
    register_api_view()
    register_api_view()


def test_register_api_view_idempotency():
    assert list(api_view.paths.keys()) == ["/api/1.0/book", "/api/1.0/book/{id}"]
