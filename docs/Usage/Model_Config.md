The [BaseModel](https://docs.pydantic.dev/latest/usage/models/) in [Pydantic](https://github.com/pydantic/pydantic)
supports some custom configurations([Model Config](https://docs.pydantic.dev/latest/usage/model_config/)),

## by_alias

Sometimes you may not want to use aliases (such as in the responses model). In that case, `by_alias` will be convenient:

```python
class MessageResponse(BaseModel):
    message: str = Field(..., description="The message")
    metadata: dict[str, str] = Field(alias="metadata_")

    model_config = dict(
        by_alias=False
    )
```