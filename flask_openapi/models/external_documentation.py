from pydantic import BaseModel


class ExternalDocumentation(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#external-documentation-object
    """

    description: str | None = None
    url: str

    model_config = {"extra": "allow"}
