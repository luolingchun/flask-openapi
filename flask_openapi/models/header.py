from .parameter import Parameter
from .parameter_in_type import ParameterInType


class Header(Parameter):
    """
    https://spec.openapis.org/oas/v3.1.0#header-object
    """

    name: str | None = None
    param_in: ParameterInType | None = None

    model_config = {"extra": "allow"}
