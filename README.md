<div align="center">
    <a href="https://luolingchun.github.io/flask-openapi/" target="_blank">
        <img class="off-glb" src="https://raw.githubusercontent.com/luolingchun/flask-openapi/main/docs/images/logo-text.svg" 
             width="60%" height="auto" alt="logo">
    </a>
</div>
<p align="center">
    <em>A simple API framework based on Flask.</em>
</p>
<p align="center">
    <a href="https://github.com/luolingchun/flask-openapi/actions/workflows/tests.yml" target="_blank">
        <img class="off-glb" src="https://img.shields.io/github/actions/workflow/status/luolingchun/flask-openapi/tests.yml?branch=master" alt="test">
    </a>
    <a href="https://pypi.org/project/flask-openapi/" target="_blank">
        <img class="off-glb" src="https://img.shields.io/pypi/v/flask-openapi" alt="pypi">
    </a>
    <a href="https://pypistats.org/packages/flask-openapi" target="_blank">
        <img class="off-glb" src="https://img.shields.io/pypi/dm/flask-openapi" alt="pypistats">
    </a>
    <a href="https://pypi.org/project/flask-openapi/" target="_blank">
        <img class="off-glb" src="https://img.shields.io/pypi/pyversions/flask-openapi" alt="pypi versions">
    </a>
</p>

**Flask OpenAPI** is a simple web API framework based on **Flask**. It uses **Pydantic** to verify data and automatic
generation of interaction documentation.

The key features are:

- **Easy to code:** Easy to use and easy to learn

- **Standard document specification:** Based on [OpenAPI Specification](https://spec.openapis.org/oas/v3.1.0)

- **Interactive OpenAPI documentation:** [Swagger](https://github.com/swagger-api/swagger-ui), [Redoc](https://github.com/Redocly/redoc), [RapiDoc](https://github.com/rapi-doc/RapiDoc), [RapiPdf](https://mrin9.github.io/RapiPdf/), [Scalar](https://github.com/scalar/scalar), [Elements](https://github.com/stoplightio/elements)

- **Data validation:** Fast data verification based on [Pydantic](https://github.com/pydantic/pydantic)

## Requirements

Python 3.11+

flask-openapi is dependent on the following libraries:

- [Flask](https://github.com/pallets/flask) for the web app.
- [Pydantic](https://github.com/pydantic/pydantic) for the data validation.

## Installation

```bash
pip install -U flask-openapi[swagger]
```

<details markdown="block">
<summary>Optional dependencies</summary>

- [python-email-validator](https://github.com/JoshData/python-email-validator) supports email verification.
- [python-dotenv](https://github.com/theskumar/python-dotenv#readme) enables support
  for [Environment Variables From dotenv](https://flask.palletsprojects.com/en/latest/cli/#dotenv) when running `flask`
  commands.
- [pyyaml](https://github.com/yaml/pyyaml) is used to output the OpenAPI document in yaml format.
- [asgiref](https://github.com/django/asgiref) allows views to be defined with `async def` and use `await`.
- [flask-openapi-plugins](https://github.com/luolingchun/flask-openapi-plugins) Provide OpenAPI UI for flask-openapi.

To install these dependencies with flask-openapi:

```bash
pip install flask-openapi[yaml]
# or
pip install flask-openapi[async]
# or
pip install flask-openapi[dotenv]
# or
pip install flask-openapi[email]
# or all
pip install flask-openapi[yaml,async,dotenv,email]
# or manually
pip install pyyaml asgiref python-dotenv email-validator
# OpenAPI UI plugins
pip install -U flask-openapi[swagger,redoc,rapidoc,rapipdf,scalar,elements]
```

</details>

## A Simple Example

Here's a simple example, further go to the [Example](https://luolingchun.github.io/flask-openapi/latest/Example/).

```python
from pydantic import BaseModel

from flask_openapi import Info, Tag
from flask_openapi import OpenAPI

info = Info(title="book API", version="1.0.0")
app = OpenAPI(__name__, info=info)

book_tag = Tag(name="book", description="Some Book")


class BookQuery(BaseModel):
    age: int
    author: str


@app.get("/book", summary="get books", tags=[book_tag])
def get_book(query: BookQuery):
    """
    to get all books
    """
    return {
        "code": 0,
        "message": "ok",
        "data": [
            {"bid": 1, "age": query.age, "author": query.author},
            {"bid": 2, "age": query.age, "author": query.author}
        ]
    }


if __name__ == "__main__":
    app.run(debug=True)
```

<details>
<summary>Class-based API View Example</summary>

```python
from pydantic import BaseModel, Field

from flask_openapi import OpenAPI, Tag, Info, APIView


info = Info(title="book API", version="1.0.0")
app = OpenAPI(__name__, info=info)

api_view = APIView(url_prefix="/api/v1", view_tags=[Tag(name="book")])


class BookPath(BaseModel):
    id: int = Field(..., description="book ID")


class BookQuery(BaseModel):
    age: int | None = Field(None, description="Age")


class BookBody(BaseModel):
    age: int | None = Field(..., ge=2, le=4, description="Age")
    author: str = Field(None, min_length=2, max_length=4, description="Author")


@api_view.route("/book")
class BookListAPIView:
    a = 1

    @api_view.doc(summary="get book list")
    def get(self, query: BookQuery):
        print(self.a)
        return query.model_dump_json()

    @api_view.doc(summary="create book")
    def post(self, body: BookBody):
        """description for a created book"""
        return body.model_dump_json()


@api_view.route("/book/<id>")
class BookAPIView:
    @api_view.doc(summary="get book")
    def get(self, path: BookPath):
        print(path)
        return "get"

    @api_view.doc(summary="update book")
    def put(self, path: BookPath):
        print(path)
        return "put"

    @api_view.doc(summary="delete book", deprecated=True)
    def delete(self, path: BookPath):
        print(path)
        return "delete"


app.register_api_view(api_view)

if __name__ == "__main__":
    app.run(debug=True)
```

</details>

## API Document

Run the [simple example](https://github.com/luolingchun/flask-openapi/blob/master/examples/simple_demo.py), and go to http://127.0.0.1:5000/openapi.

> OpenAPI UI plugins are optional dependencies that require manual installation.
>
> `pip install -U flask-openapi[swagger,redoc,rapidoc,rapipdf,scalar,elements]`
>
> More optional ui templates goto the document
> about [UI_Templates](https://luolingchun.github.io/flask-openapi/latest/Usage/UI_Templates/).

![openapi](https://raw.githubusercontent.com/luolingchun/flask-openapi/main/docs/images/openapi-all.png)
