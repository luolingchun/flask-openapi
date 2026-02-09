from pydantic import BaseModel, Field


class Reference(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#reference-object
    """

    ref: str = Field(..., alias="$ref")

    model_config = {"extra": "allow", "populate_by_name": True}
