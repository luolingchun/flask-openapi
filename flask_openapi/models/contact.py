from pydantic import BaseModel


class Contact(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#contact-object
    """

    name: str | None = None
    url: str | None = None
    email: str | None = None

    model_config = {"extra": "allow"}
