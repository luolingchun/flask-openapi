import inspect
import posixpath
import re
from http import HTTPMethod, HTTPStatus
from typing import Any, Callable, DefaultDict, Type, get_type_hints

from flask import current_app, make_response
from flask.wrappers import Response as FlaskResponse
from pydantic import BaseModel, ValidationError
from pydantic.json_schema import JsonSchemaMode

from .models import (
    OPENAPI3_REF_PREFIX,
    OPENAPI3_REF_TEMPLATE,
    Encoding,
    MediaType,
    Operation,
    Parameter,
    ParameterInType,
    PathItem,
    RequestBody,
    Response,
    Schema,
    Tag,
)
from .types import ParametersTuple, ResponseDict, ResponseStrKeyDict

HTTP_STATUS = {str(status.value): status.phrase for status in HTTPStatus}


def get_operation(
    func: Callable,
    *,
    summary: str | None = None,
    description: str | None = None,
    openapi_extensions: dict[str, Any] | None = None,
) -> Operation:
    """
    Return an Operation object with the specified summary and description.

    Args:
        func: The function or method for which the operation is being defined.
        summary: A short summary of what the operation does.
        description: A verbose explanation of the operation behavior.
        openapi_extensions: Additional extensions to the OpenAPI Schema.

    Returns:
        An Operation object representing the operation.

    """
    # Get the docstring of the function
    doc = inspect.getdoc(func) or ""
    doc = doc.strip()
    lines = doc.split("\n")

    doc_summary = lines[0]
    doc_description = "<br/>".join(lines) if summary else "<br/>".join(lines[1:])

    summary = summary or doc_summary
    description = description or doc_description

    # Create the operation dictionary with summary and description
    operation_dict = {}

    if summary:
        operation_dict["summary"] = summary

    if description:
        operation_dict["description"] = description

    # Add any additional openapi_extensions to the operation dictionary
    operation_dict.update(openapi_extensions or {})

    # Create and return the Operation object
    operation = Operation(**operation_dict)

    return operation


def get_operation_id_for_path(*, bp_name: str = "", name: str = "", path: str = "", method: str = "") -> str:
    """
    Generate a unique operation ID based on the name, path, and method.

    Args:
        name: The name or identifier for the operation.
        path: The URL path for the operation.
        method: The HTTP method for the operation.
        bp_name: The Blueprint name

    Returns:
        A unique operation ID generated based on the provided name, path, and method.

    """
    if bp_name:
        name = bp_name + "_" + name
    return re.sub(r"\W", "_", name + path) + "_" + method.lower()


def get_model_schema(model: Type[BaseModel], mode: JsonSchemaMode = "validation") -> dict:
    """Converts a Pydantic model to an OpenAPI schema."""

    assert inspect.isclass(model) and issubclass(model, BaseModel), f"{model} is invalid `pydantic.BaseModel`"

    model_config: DefaultDict[str, Any] = model.model_config  # type: ignore
    by_alias = bool(model_config.get("by_alias", True))

    return model.model_json_schema(by_alias=by_alias, ref_template=OPENAPI3_REF_TEMPLATE, mode=mode)


def parse_header(header: Type[BaseModel]) -> tuple[list[Parameter], dict]:
    """Parses a header model and returns a list of parameters and component schemas."""
    schema = get_model_schema(header)
    parameters = []
    components_schemas: dict = dict()
    properties = schema.get("properties", {})

    for name, value in properties.items():
        data = {
            "name": name,
            "in": ParameterInType.HEADER,
            "required": name in schema.get("required", []),
            "schema": Schema(**value),
        }
        # Parse extra values
        if "description" in value.keys():
            data["description"] = value.get("description")
        if "deprecated" in value.keys():
            data["deprecated"] = value.get("deprecated")
        if "example" in value.keys():
            data["example"] = value.get("example")
        if "examples" in value.keys():
            data["examples"] = value.get("examples")
        parameters.append(Parameter.model_validate(data))

    # Parse definitions
    definitions = schema.get("$defs", {})
    for name, value in definitions.items():
        components_schemas[name] = Schema(**value)

    return parameters, components_schemas


def parse_cookie(cookie: Type[BaseModel]) -> tuple[list[Parameter], dict]:
    """Parses a cookie model and returns a list of parameters and component schemas."""
    schema = get_model_schema(cookie)
    parameters = []
    components_schemas: dict = dict()
    properties = schema.get("properties", {})

    for name, value in properties.items():
        data = {
            "name": name,
            "in": ParameterInType.COOKIE,
            "required": name in schema.get("required", []),
            "schema": Schema(**value),
        }
        # Parse extra values
        if "description" in value.keys():
            data["description"] = value.get("description")
        if "deprecated" in value.keys():
            data["deprecated"] = value.get("deprecated")
        if "example" in value.keys():
            data["example"] = value.get("example")
        if "examples" in value.keys():
            data["examples"] = value.get("examples")
        parameters.append(Parameter.model_validate(data))

    # Parse definitions
    definitions = schema.get("$defs", {})
    for name, value in definitions.items():
        components_schemas[name] = Schema(**value)

    return parameters, components_schemas


def parse_path(path: Type[BaseModel]) -> tuple[list[Parameter], dict]:
    """Parses a path model and returns a list of parameters and component schemas."""
    schema = get_model_schema(path)
    parameters = []
    components_schemas: dict = dict()
    properties = schema.get("properties", {})

    for name, value in properties.items():
        data = {"name": name, "in": ParameterInType.PATH, "required": True, "schema": Schema(**value)}
        # Parse extra values
        if "description" in value.keys():
            data["description"] = value.get("description")
        if "deprecated" in value.keys():
            data["deprecated"] = value.get("deprecated")
        if "example" in value.keys():
            data["example"] = value.get("example")
        if "examples" in value.keys():
            data["examples"] = value.get("examples")
        parameters.append(Parameter.model_validate(data))

    # Parse definitions
    definitions = schema.get("$defs", {})
    for name, value in definitions.items():
        components_schemas[name] = Schema(**value)

    return parameters, components_schemas


def parse_query(query: Type[BaseModel]) -> tuple[list[Parameter], dict]:
    """Parses a query model and returns a list of parameters and component schemas."""
    schema = get_model_schema(query)
    parameters = []
    components_schemas: dict = dict()
    properties = schema.get("properties", {})

    for name, value in properties.items():
        data = {
            "name": name,
            "in": ParameterInType.QUERY,
            "required": name in schema.get("required", []),
            "schema": Schema(**value),
        }
        # Parse extra values
        if "description" in value.keys():
            data["description"] = value.get("description")
        if "deprecated" in value.keys():
            data["deprecated"] = value.get("deprecated")
        if "example" in value.keys():
            data["example"] = value.get("example")
        if "examples" in value.keys():
            data["examples"] = value.get("examples")
        parameters.append(Parameter.model_validate(data))

    # Parse definitions
    definitions = schema.get("$defs", {})
    for name, value in definitions.items():
        components_schemas[name] = Schema(**value)

    return parameters, components_schemas


def parse_form(form: Type[BaseModel]) -> tuple[dict[str, MediaType], dict]:
    """Parses a form model and returns a list of parameters and component schemas."""
    schema = get_model_schema(form)
    components_schemas = dict()
    properties = schema.get("properties", {})

    assert properties, f"{form.__name__}'s properties cannot be empty."

    original_title = schema.get("title") or form.__name__
    title = normalize_name(original_title)
    components_schemas[title] = Schema(**schema)
    encoding = {}
    for k, v in properties.items():
        if v.get("type") == "array":
            encoding[k] = Encoding(style="form", explode=True)
    content = {"multipart/form-data": MediaType.model_validate({"schema": {"$ref": f"{OPENAPI3_REF_PREFIX}/{title}"}})}
    if encoding:
        content["multipart/form-data"].encoding = encoding

    # Parse definitions
    definitions = schema.get("$defs", {})
    for name, value in definitions.items():
        components_schemas[name] = Schema(**value)

    return content, components_schemas


def parse_body(body: Type[BaseModel]) -> tuple[dict[str, MediaType], dict]:
    """Parses a body model and returns a list of parameters and component schemas."""
    schema = get_model_schema(body)
    components_schemas = dict()

    original_title = schema.get("title") or body.__name__
    title = normalize_name(original_title)
    components_schemas[title] = Schema(**schema)
    content = {"application/json": MediaType.model_validate({"schema": {"$ref": f"{OPENAPI3_REF_PREFIX}/{title}"}})}

    # Parse definitions
    definitions = schema.get("$defs", {})
    for name, value in definitions.items():
        components_schemas[name] = Schema(**value)

    return content, components_schemas


def get_responses(responses: ResponseStrKeyDict, components_schemas: dict, operation: Operation) -> None:
    _responses = {}
    _schemas = {}

    for key, response in responses.items():
        if response is None:
            # If the response is None, it means HTTP status code "204" (No Content)
            _responses[key] = Response(description=HTTP_STATUS.get(key, ""))
        elif isinstance(response, dict):
            response["description"] = response.get("description", HTTP_STATUS.get(key, ""))
            _responses[key] = Response(**response)
        elif isinstance(response, Response):
            _responses[key] = response
        else:
            # OpenAPI 3 support ^[a-zA-Z0-9\.\-_]+$ so we should normalize __name__
            schema = get_model_schema(response, mode="serialization")
            original_title = schema.get("title") or response.__name__
            name = normalize_name(original_title)
            _responses[key] = Response(description=HTTP_STATUS.get(key, ""))
            _responses[key].content = {
                "application/json": MediaType.model_validate({"schema": {"$ref": f"{OPENAPI3_REF_PREFIX}/{name}"}})
            }

            _schemas[name] = Schema(**schema)
            definitions = schema.get("$defs")
            if definitions:
                # Add schema definitions to _schemas
                for name, value in definitions.items():
                    _schemas[normalize_name(name)] = Schema(**value)

    components_schemas.update(**_schemas)
    operation.responses = _responses


def parse_and_store_tags(
    new_tags: list[Tag | dict[str, Any]],
    old_tags: list[Tag],
    old_tag_names: list[str],
    operation: Operation,
) -> None:
    """
    Parses new tags, stores them in an old_tags list if they are not already present,
    and updates the tags attribute of the operation object.

    Args:
        new_tags: A list of new Tag objects to be parsed and stored.
        old_tags: The list of existing Tag objects.
        old_tag_names: The list that names of existing tags.
        operation: The operation object whose tag attribute needs to be updated.

    Returns:
        None
    """
    new_tag_names = []
    # Iterate over each tag in new_tags
    for tag in new_tags:
        if isinstance(tag, dict):
            tag = Tag(**tag)
        new_tag_names.append(tag.name)
        if tag.name not in old_tag_names:
            old_tag_names.append(tag.name)
            old_tags.append(tag)

    # Set the tags attribute of the operation object to a list of unique tag names from new_tags
    # If the resulting list is empty, set it to ["default"]
    operation.tags = list(set(new_tag_names)) or ["default"]


def parse_parameters(
    func: Callable,
    *,
    components_schemas: dict | None = None,
    operation: Operation | None = None,
    request_body: RequestBody | None = None,
    doc_ui: bool = True,
) -> ParametersTuple:
    # If components_schemas is None, initialize it as an empty dictionary
    if components_schemas is None:
        components_schemas = dict()

    # If operation is None, initialize it as an Operation object
    if operation is None:
        operation = Operation()

    # Get the type hints from the function
    annotations = get_type_hints(func)

    # Get the types for header, cookie, path, query, form, and body parameters
    header: Type[BaseModel] | None = annotations.get("header")
    cookie: Type[BaseModel] | None = annotations.get("cookie")
    path: Type[BaseModel] | None = annotations.get("path")
    query: Type[BaseModel] | None = annotations.get("query")
    form: Type[BaseModel] | None = annotations.get("form")
    body: Type[BaseModel] | None = annotations.get("body")

    # If doc_ui is False, return the types without further processing
    if not doc_ui:
        return header, cookie, path, query, form, body

    parameters = []
    _request_body = None

    if header:
        _parameters, _components_schemas = parse_header(header)
        parameters.extend(_parameters)
        components_schemas.update(**_components_schemas)

    if cookie:
        _parameters, _components_schemas = parse_cookie(cookie)
        parameters.extend(_parameters)
        components_schemas.update(**_components_schemas)

    if path:
        _parameters, _components_schemas = parse_path(path)
        parameters.extend(_parameters)
        components_schemas.update(**_components_schemas)

    if query:
        _parameters, _components_schemas = parse_query(query)
        parameters.extend(_parameters)
        components_schemas.update(**_components_schemas)

    if form:
        _content, _components_schemas = parse_form(form)
        components_schemas.update(**_components_schemas)
        _request_body = RequestBody(content=_content, required=True)

    if body:
        _content, _components_schemas = parse_body(body)
        components_schemas.update(**_components_schemas)
        _request_body = RequestBody(content=_content, required=True)

    if parameters:
        # Set the parsed parameters in the operation object
        operation.parameters = parameters

    operation.requestBody = request_body or _request_body

    return header, cookie, path, query, form, body


def parse_method(uri: str, method: str, paths: dict, operation: Operation) -> None:
    """
    Parses the HTTP method and updates the corresponding PathItem object in the paths' dictionary.

    Args:
        uri: The URI of the API endpoint.
        method: The HTTP method for the API endpoint.
        paths: A dictionary containing the API paths and their corresponding PathItem objects.
        operation: The Operation object to assign to the PathItem.

    Returns:
        None
    """
    # Check the HTTP method and update the PathItem object in the path dictionary
    if method == HTTPMethod.GET:
        paths.setdefault(uri, PathItem()).get = operation
    elif method == HTTPMethod.POST:
        paths.setdefault(uri, PathItem()).post = operation
    elif method == HTTPMethod.PUT:
        paths.setdefault(uri, PathItem()).put = operation
    elif method == HTTPMethod.PATCH:
        paths.setdefault(uri, PathItem()).patch = operation
    elif method == HTTPMethod.DELETE:
        paths.setdefault(uri, PathItem()).delete = operation


def make_validation_error_response(e: ValidationError) -> FlaskResponse:
    """
    Create a Flask response for a validation error.

    Args:
        e: The ValidationError object containing the details of the error.

    Returns:
        FlaskResponse: A Flask Response object with the JSON representation of the error.
    """
    response = make_response(e.json())
    response.headers["Content-Type"] = "application/json"
    response.status_code = getattr(current_app, "validation_error_status", 422)
    return response


def run_validate_response(response: Any, responses: ResponseDict) -> Any:
    """Validate response"""

    if isinstance(response, tuple):
        _resp, status_code = response[:2]
    elif isinstance(response, FlaskResponse):
        if response.mimetype != "application/json":
            # only application/json
            return response
        _resp, status_code = response.json, response.status_code
    else:
        _resp, status_code = response, 200

    # status_code is http.HTTPStatus
    if isinstance(status_code, HTTPStatus):
        status_code = status_code.value

    resp_model = responses.get(status_code)

    if resp_model is None:
        return response

    assert inspect.isclass(resp_model) and issubclass(resp_model, BaseModel), (
        f"{resp_model} is invalid `pydantic.BaseModel`"
    )

    if isinstance(_resp, str):
        resp_model.model_validate_json(_resp)
    else:
        resp_model.model_validate(_resp)

    return response


def parse_rule(rule: str, url_prefix=None) -> str:
    # Merge url_prefix and uri
    if rule:
        uri = posixpath.join(url_prefix, rule.lstrip("/")) if url_prefix else rule
    else:
        uri = url_prefix or ""

    # Convert a route parameter format from /pet/<petId> to /pet/{petId}
    uri = re.sub(r"<([^<:]+:)?", "{", uri).replace(">", "}")

    return uri


def convert_responses_key_to_string(responses: ResponseDict) -> ResponseStrKeyDict:
    """Convert key to string"""

    return {str(key.value if isinstance(key, HTTPStatus) else key): value for key, value in responses.items()}


def normalize_name(name: str) -> str:
    return re.sub(r"[^\w.\-]", "_", name)
