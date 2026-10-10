from pydantic import BaseModel


class OAuthFlow(BaseModel):
    """
    https://spec.openapis.org/oas/v3.2.0#oauth-flow-object
    """

    authorizationUrl: str | None = None
    tokenUrl: str | None = None
    refreshUrl: str | None = None
    deviceAuthorizationUrl: str | None = None
    scopes: dict[str, str]

    model_config = {"extra": "allow"}
