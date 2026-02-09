from enum import Enum


class ParameterInType(str, Enum):
    """The place Parameters can be put when calling an Endpoint"""

    QUERY = "query"
    PATH = "path"
    HEADER = "header"
    COOKIE = "cookie"
