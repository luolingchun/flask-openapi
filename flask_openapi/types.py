from http import HTTPStatus
from typing import Any, Type

from pydantic import BaseModel

_ResponseDictValue = Type[BaseModel] | dict[Any, Any] | None

ResponseDict = dict[str | int | HTTPStatus, _ResponseDictValue]

ResponseStrKeyDict = dict[str, _ResponseDictValue]

ParametersTuple = tuple[
    Type[BaseModel] | None,
    Type[BaseModel] | None,
    Type[BaseModel] | None,
    Type[BaseModel] | None,
    Type[BaseModel] | None,
    Type[BaseModel] | None,
]
