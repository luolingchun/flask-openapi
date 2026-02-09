from enum import Enum


class SecuritySchemeInType(str, Enum):
    """The place Parameters can be put when calling an Endpoint"""

    QUERY = "query"
    HEADER = "header"
    COOKIE = "cookie"
