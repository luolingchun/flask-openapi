from enum import Enum


class DataType(str, Enum):
    """
    https://spec.openapis.org/oas/v3.2.0#data-types
    """

    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    NUll = "null"
