from typing import TYPE_CHECKING, Union

from pydantic import BaseModel

from .reference import Reference

if TYPE_CHECKING:  # pragma: no cover
    from .header import Header
else:
    Header = "Header"


class Encoding(BaseModel):
    """
    https://spec.openapis.org/oas/v3.2.0#encoding-object
    """

    contentType: str | None = None
    headers: dict[str, Union[Header, Reference]] | None = None
    style: str | None = None
    explode: bool | None = None
    allowReserved: bool = False
    prefixEncoding: Union["Encoding", Reference] | None = None
    itemEncoding: Union["Encoding", Reference] | None = None

    model_config = {"extra": "allow"}
