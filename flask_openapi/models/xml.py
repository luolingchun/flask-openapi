from pydantic import BaseModel


class XML(BaseModel):
    """
    https://spec.openapis.org/oas/v3.2.0#xml-object
    """

    name: str | None = None
    namespace: str | None = None
    prefix: str | None = None
    attribute: bool = False
    wrapped: bool = False
    nodeType: str | None = None

    model_config = {"extra": "allow"}
