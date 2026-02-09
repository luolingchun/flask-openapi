import inspect
from types import FunctionType
from typing import Any, Callable

from flask import Blueprint

from .endpoint import create_view_func
from .models import ExternalDocumentation, Server, Tag
from .types import ParametersTuple, ResponseDict
from .utils import (
    HTTPMethod,
    convert_responses_key_to_string,
    get_operation,
    get_operation_id_for_path,
    get_responses,
    parse_and_store_tags,
    parse_method,
    parse_parameters,
    parse_rule,
)


class APIBlueprint(Blueprint):
    def __init__(
        self,
        name: str,
        import_name: str,
        *,
        abp_tags: list[Tag | dict[str, Any]] | None = None,
        abp_security: list[dict[str, list[str]]] | None = None,
        abp_responses: ResponseDict | None = None,
        doc_ui: bool = True,
        operation_id_callback: Callable = get_operation_id_for_path,
        validate_response: bool | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Based on Flask Blueprint

        Args:
            name: The name of the blueprint. It Will be prepared to each endpoint name.
            import_name: The name of the blueprint package, usually ``__name__``.
                         This helps locate the ``root_path`` for the blueprint.
            abp_tags: APIBlueprint tags for every API.
            abp_security: APIBlueprint security for every API.
            abp_responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            doc_ui: Enable OpenAPI document UI (Swagger UI, Redoc, and Rapidoc). Defaults to True.
            operation_id_callback: Callback function for custom operation_id generation.
                                   Receives name (str), path (str) and method (str) parameters.
                                   Defaults to `get_operation_id_for_path` from utils
            validate_response: Verify the response body.
            **kwargs: Flask Blueprint kwargs
        """
        super(APIBlueprint, self).__init__(name, import_name, **kwargs)

        # Initialize instance variables
        self.paths: dict = dict()
        self.components_schemas: dict = dict()
        self.tags: list[Tag] = []
        self.tag_names: list[str] = []

        # Set values from arguments or default values
        self.abp_tags = abp_tags or []
        self.abp_security = abp_security or []

        # Convert key to string
        self.abp_responses = convert_responses_key_to_string(abp_responses or {})

        self.doc_ui = doc_ui

        # Set the operation ID callback function
        self.operation_id_callback: Callable = operation_id_callback

        # Verify the response body
        self.validate_response = validate_response

    def register_api(self, api: "APIBlueprint") -> None:
        """Register a nested APIBlueprint"""

        # Check if the APIBlueprint is being registered on itself
        if api is self:
            raise ValueError("Cannot register a api blueprint on itself")

        # Merge tags from the nested APIBlueprint
        for tag in api.tags:
            if tag.name not in self.tag_names:
                self.tags.append(tag)
                self.tag_names.append(tag.name)

        # Merge paths from the nested APIBlueprint
        for path_url, path_item in api.paths.items():
            # Parse rule: merge url_prefix and format rule from /pet/<petId> to /pet/{petId}
            uri = parse_rule(path_url, url_prefix=self.url_prefix)

            self.paths[uri] = path_item

        # Merge component schemas from the nested APIBlueprint
        self.components_schemas.update(api.components_schemas)

        # Register the nested APIBlueprint as a blueprint
        self.register_blueprint(api)

    def _add_url_rule(
        self,
        rule,
        endpoint=None,
        view_func=None,
        provide_automatic_options=None,
        **options,
    ) -> None:
        self.add_url_rule(rule, endpoint, view_func, provide_automatic_options, **options)

    def _collect_openapi_info(
        self,
        rule: str,
        func: FunctionType,
        *,
        tags: list[Tag] | None = None,
        summary: str | None = None,
        description: str | None = None,
        external_docs: ExternalDocumentation | None = None,
        operation_id: str | None = None,
        responses: ResponseDict | None = None,
        deprecated: bool | None = None,
        security: list[dict[str, list[Any]]] | None = None,
        servers: list[Server] | None = None,
        openapi_extensions: dict[str, Any] | None = None,
        doc_ui: bool = True,
        method: str = HTTPMethod.GET,
    ) -> ParametersTuple:
        """
        Collects OpenAPI specification information for Flask routes and view functions.

        Args:
            rule: Flask route
            func: Flask view_func
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            doc_ui: Declares this operation to be shown. Default to True.
        """
        if self.doc_ui is True and doc_ui is True:
            # Convert key to string
            new_responses = convert_responses_key_to_string(responses or {})

            # Global response: combine API responses
            combine_responses = {**self.abp_responses, **new_responses}

            # Create operation
            operation = get_operation(
                func, summary=summary, description=description, openapi_extensions=openapi_extensions
            )

            # Set external docs
            if external_docs:
                operation.externalDocs = external_docs

            # Unique string used to identify the operation.
            operation_id_kwargs = {"name": func.__name__, "path": rule, "method": method}
            if "bp_name" in list(inspect.signature(self.operation_id_callback).parameters.keys()):
                operation_id_kwargs["bp_name"] = self.name
            operation.operationId = operation_id or self.operation_id_callback(**operation_id_kwargs)

            # Only set `deprecated` if True, otherwise leave it as None
            if deprecated is not None:
                operation.deprecated = deprecated

            # Add security
            _security = (security or []) + self.abp_security or None
            if _security:
                operation.security = _security

            # Add servers
            if servers:
                operation.servers = servers

            # Store tags
            tags = (tags or []) + self.abp_tags
            parse_and_store_tags(tags, self.tags, self.tag_names, operation)

            # Parse response
            get_responses(combine_responses, self.components_schemas, operation)

            # Parse rule: merge url_prefix and format rule from /pet/<petId> to /pet/{petId}
            uri = parse_rule(rule, url_prefix=self.url_prefix)

            # Parse method
            parse_method(uri, method, self.paths, operation)

            # Parse parameters
            return parse_parameters(func, components_schemas=self.components_schemas, operation=operation)
        else:
            return parse_parameters(func, doc_ui=False)

    def get(
        self,
        rule: str,
        *,
        tags: list[Tag] | None = None,
        summary: str | None = None,
        description: str | None = None,
        external_docs: ExternalDocumentation | None = None,
        operation_id: str | None = None,
        deprecated: bool | None = None,
        security: list[dict[str, list[Any]]] | None = None,
        servers: list[Server] | None = None,
        openapi_extensions: dict[str, Any] | None = None,
        responses: ResponseDict | None = None,
        validate_response: bool | None = None,
        doc_ui: bool = True,
        **options: Any,
    ) -> Callable:
        """
        Decorator for defining a REST API endpoint with the HTTP GET method.
        More information goto https://spec.openapis.org/oas/v3.1.0#operation-object

        Args:
            rule: The URL rule string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            validate_response: Verify the response body.
            doc_ui: Declares this operation to be shown. Default to True.
        """

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body = self._collect_openapi_info(
                rule,
                func,
                tags=tags,
                summary=summary,
                description=description,
                external_docs=external_docs,
                operation_id=operation_id,
                responses=responses,
                deprecated=deprecated,
                security=security,
                servers=servers,
                openapi_extensions=openapi_extensions,
                doc_ui=doc_ui,
                method=HTTPMethod.GET,
            )

            view_func = create_view_func(
                func,
                header,
                cookie,
                path,
                query,
                form,
                body,
                responses=responses,
                validate_response=validate_response or self.validate_response,
            )

            options.update({"methods": [HTTPMethod.GET]})
            self.add_url_rule(rule, view_func=view_func, **options)

            return func

        return decorator

    def post(
        self,
        rule: str,
        *,
        tags: list[Tag] | None = None,
        summary: str | None = None,
        description: str | None = None,
        external_docs: ExternalDocumentation | None = None,
        operation_id: str | None = None,
        deprecated: bool | None = None,
        security: list[dict[str, list[Any]]] | None = None,
        servers: list[Server] | None = None,
        openapi_extensions: dict[str, Any] | None = None,
        responses: ResponseDict | None = None,
        validate_response: bool | None = None,
        doc_ui: bool = True,
        **options: Any,
    ) -> Callable:
        """
        Decorator for defining a REST API endpoint with the HTTP POST method.
        More information goto https://spec.openapis.org/oas/v3.1.0#operation-object

        Args:
            rule: The URL rule string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            validate_response: Verify the response body.
            doc_ui: Declares this operation to be shown. Default to True.
        """

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body = self._collect_openapi_info(
                rule,
                func,
                tags=tags,
                summary=summary,
                description=description,
                external_docs=external_docs,
                operation_id=operation_id,
                responses=responses,
                deprecated=deprecated,
                security=security,
                servers=servers,
                openapi_extensions=openapi_extensions,
                doc_ui=doc_ui,
                method=HTTPMethod.POST,
            )

            view_func = create_view_func(
                func,
                header,
                cookie,
                path,
                query,
                form,
                body,
                responses=responses,
                validate_response=validate_response or self.validate_response,
            )

            options.update({"methods": [HTTPMethod.POST]})
            self.add_url_rule(rule, view_func=view_func, **options)

            return func

        return decorator

    def put(
        self,
        rule: str,
        *,
        tags: list[Tag] | None = None,
        summary: str | None = None,
        description: str | None = None,
        external_docs: ExternalDocumentation | None = None,
        operation_id: str | None = None,
        deprecated: bool | None = None,
        security: list[dict[str, list[Any]]] | None = None,
        servers: list[Server] | None = None,
        openapi_extensions: dict[str, Any] | None = None,
        responses: ResponseDict | None = None,
        validate_response: bool | None = None,
        doc_ui: bool = True,
        **options: Any,
    ) -> Callable:
        """
        Decorator for defining a REST API endpoint with the HTTP PUT method.
        More information goto https://spec.openapis.org/oas/v3.1.0#operation-object

        Args:
            rule: The URL rule string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            validate_response: Verify the response body.
            doc_ui: Declares this operation to be shown. Default to True.
        """

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body = self._collect_openapi_info(
                rule,
                func,
                tags=tags,
                summary=summary,
                description=description,
                external_docs=external_docs,
                operation_id=operation_id,
                responses=responses,
                deprecated=deprecated,
                security=security,
                servers=servers,
                openapi_extensions=openapi_extensions,
                doc_ui=doc_ui,
                method=HTTPMethod.PUT,
            )

            view_func = create_view_func(
                func,
                header,
                cookie,
                path,
                query,
                form,
                body,
                responses=responses,
                validate_response=validate_response or self.validate_response,
            )

            options.update({"methods": [HTTPMethod.PUT]})
            self.add_url_rule(rule, view_func=view_func, **options)

            return func

        return decorator

    def delete(
        self,
        rule: str,
        *,
        tags: list[Tag] | None = None,
        summary: str | None = None,
        description: str | None = None,
        external_docs: ExternalDocumentation | None = None,
        operation_id: str | None = None,
        deprecated: bool | None = None,
        security: list[dict[str, list[Any]]] | None = None,
        servers: list[Server] | None = None,
        openapi_extensions: dict[str, Any] | None = None,
        responses: ResponseDict | None = None,
        validate_response: bool | None = None,
        doc_ui: bool = True,
        **options: Any,
    ) -> Callable:
        """
        Decorator for defining a REST API endpoint with the HTTP DELETE method.
        More information goto https://spec.openapis.org/oas/v3.1.0#operation-object

        Args:
            rule: The URL rule string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            validate_response: Verify the response body.
            doc_ui: Declares this operation to be shown. Default to True.
        """

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body = self._collect_openapi_info(
                rule,
                func,
                tags=tags,
                summary=summary,
                description=description,
                external_docs=external_docs,
                operation_id=operation_id,
                responses=responses,
                deprecated=deprecated,
                security=security,
                servers=servers,
                openapi_extensions=openapi_extensions,
                doc_ui=doc_ui,
                method=HTTPMethod.DELETE,
            )

            view_func = create_view_func(
                func,
                header,
                cookie,
                path,
                query,
                form,
                body,
                responses=responses,
                validate_response=validate_response or self.validate_response,
            )

            options.update({"methods": [HTTPMethod.DELETE]})
            self.add_url_rule(rule, view_func=view_func, **options)

            return func

        return decorator

    def patch(
        self,
        rule: str,
        *,
        tags: list[Tag] | None = None,
        summary: str | None = None,
        description: str | None = None,
        external_docs: ExternalDocumentation | None = None,
        operation_id: str | None = None,
        deprecated: bool | None = None,
        security: list[dict[str, list[Any]]] | None = None,
        servers: list[Server] | None = None,
        openapi_extensions: dict[str, Any] | None = None,
        responses: ResponseDict | None = None,
        validate_response: bool | None = None,
        doc_ui: bool = True,
        **options: Any,
    ) -> Callable:
        """
        Decorator for defining a REST API endpoint with the HTTP PATCH method.
        More information goto https://spec.openapis.org/oas/v3.1.0#operation-object

        Args:
            rule: The URL rule string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            validate_response: Verify the response body.
            doc_ui: Declares this operation to be shown. Default to True.
        """

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body = self._collect_openapi_info(
                rule,
                func,
                tags=tags,
                summary=summary,
                description=description,
                external_docs=external_docs,
                operation_id=operation_id,
                responses=responses,
                deprecated=deprecated,
                security=security,
                servers=servers,
                openapi_extensions=openapi_extensions,
                doc_ui=doc_ui,
                method=HTTPMethod.PATCH,
            )

            view_func = create_view_func(
                func,
                header,
                cookie,
                path,
                query,
                form,
                body,
                responses=responses,
                validate_response=validate_response or self.validate_response,
            )

            options.update({"methods": [HTTPMethod.PATCH]})
            self.add_url_rule(rule, view_func=view_func, **options)

            return func

        return decorator
