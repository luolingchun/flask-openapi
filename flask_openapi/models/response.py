from pydantic import BaseModel

from .header import Header
from .link import Link
from .media_type import MediaType
from .reference import Reference


class Response(BaseModel):
    """
    https://spec.openapis.org/oas/v3.2.0#response-object
    """

    description: str | None = None
    summary: str | None = None
    headers: dict[str, Header | Reference] | None = None
    content: dict[str, MediaType] | None = None
    links: dict[str, Link | Reference] | None = None

    model_config = {"extra": "allow"}
