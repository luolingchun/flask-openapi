from pydantic import BaseModel


class Discriminator(BaseModel):
    """
    https://spec.openapis.org/oas/v3.2.0#discriminator-object
    """

    propertyName: str | None = None
    mapping: dict[str, str] | None = None
    defaultMapping: str | None = None

    model_config = {"extra": "allow"}
