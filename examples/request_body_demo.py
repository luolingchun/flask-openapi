from flask import request
from pydantic import BaseModel

from flask_openapi import OpenAPI, RequestBody
from flask_openapi.utils import get_model_schema

app = OpenAPI(__name__)


class BookModel(BaseModel):
    name: str
    age: int


request_body_json = RequestBody(
    description="The json request body",
    content={"application/custom+json": {"schema": get_model_schema(BookModel)}},
)


@app.post("/json", request_body=request_body_json)
def post_json(body: BookModel):
    print(request.headers.get("content-type"))
    print(body.model_json_schema())
    return {"message": "Hello World"}


request_body = RequestBody(
    description="The multi request body",
    content={
        "text/plain": {"schema": {"type": "string"}},
        "text/html": {"schema": {"type": "string"}},
        "image/png": {"schema": {"type": "string", "format": "binary"}},
    },
)


@app.post("/text", request_body=request_body)
def post_csv():
    print(request.headers.get("content-type"))
    data = request.data
    print(data)
    return {"message": "Hello World"}


if __name__ == "__main__":
    print(app.url_map)
    app.run()
