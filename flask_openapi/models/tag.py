from pydantic import BaseModel

from .external_documentation import ExternalDocumentation


class Tag(BaseModel):
    """
    https://spec.openapis.org/oas/v3.2.0#tag-object
    """

    name: str
    description: str | None = None
    summary: str | None = None
    parent: str | None = None
    kind: str | None = None
    externalDocs: ExternalDocumentation | None = None

    model_config = {"extra": "allow"}
