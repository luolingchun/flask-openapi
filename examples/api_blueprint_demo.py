from pydantic import BaseModel, Field

from flask_openapi import APIBlueprint, Info, OpenAPI, Tag

info = Info(title="book API", version="1.0.0")

jwt = {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
security_schemes = {"jwt": jwt}

app = OpenAPI(__name__, info=info, security_schemes=security_schemes)

tag = Tag(name="book", description="Some Book")
security = [{"jwt": []}]


class Unauthorized(BaseModel):
    code: int = Field(-1, description="Status Code")
    message: str = Field("Unauthorized!", description="Exception Information")


api = APIBlueprint(
    "/book",
    __name__,
    url_prefix="/api",
    abp_tags=[tag],
    abp_security=security,
    abp_responses={"401": Unauthorized},
    # disable openapi UI
    doc_ui=True,
)


class BookBody(BaseModel):
    age: int | None = Field(3, ge=2, le=4, description="Age")
    author: str = Field("xxx", min_length=2, max_length=4, description="Author")


class Path(BaseModel):
    id: int = Field(1, description="book id")


@api.get("/book", doc_ui=False)
def get_book():
    return {"code": 0, "message": "ok"}


@api.post("/book", responses={200: {"content": {"text/csv": {"schema": {"type": "string"}}}}})
def create_book(body: BookBody):
    assert body.age == 3
    return {"code": 0, "message": "ok"}


@api.put("/book/<id>", operation_id="update")
def update_book(path: Path, body: BookBody):
    assert path.id == 1
    assert body.age == 3
    return {"code": 0, "message": "ok"}


# register api
app.register_api(api)

if __name__ == "__main__":
    app.run(debug=True)
