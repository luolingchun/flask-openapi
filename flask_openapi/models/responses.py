from .reference import Reference
from .response import Response

"""
https://spec.openapis.org/oas/v3.1.0#responses-object
"""
Responses = dict[str, Response | Reference]
