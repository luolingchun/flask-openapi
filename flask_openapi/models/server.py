from pydantic import BaseModel

from .server_variable import ServerVariable


class Server(BaseModel):
    """
    https://spec.openapis.org/oas/v3.2.0#server-object
    """

    url: str
    name: str | None = None
    description: str | None = None
    variables: dict[str, ServerVariable] | None = None

    model_config = {"extra": "allow"}
