from pydantic import BaseModel


class Discriminator(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#discriminator-object
    """

    propertyName: str
    mapping: dict[str, str] | None = None

    model_config = {"extra": "allow"}
