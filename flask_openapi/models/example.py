from typing import Any

from pydantic import BaseModel


class Example(BaseModel):
    """
    https://spec.openapis.org/oas/v3.2.0#example-object
    """

    summary: str | None = None
    description: str | None = None
    value: Any | None = None
    dataValue: Any | None = None
    serializedValue: Any | None = None
    externalValue: str | None = None

    model_config = {"extra": "allow"}
