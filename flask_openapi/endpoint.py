import inspect
from functools import wraps

from flask import current_app
from flask.wrappers import Response as FlaskResponse

from .request import _validate_request
from .types import ResponseDict


def create_view_func(
    func,
    header,
    cookie,
    path,
    query,
    form,
    body,
    view_class=None,
    view_kwargs=None,
    responses: ResponseDict | None = None,
    validate_response: bool | None = None,
):
    is_coroutine_function = inspect.iscoroutinefunction(func)
    if is_coroutine_function:

        @wraps(func)
        async def view_func(**kwargs) -> FlaskResponse:
            if hasattr(func, "__delay_validate_request__") and func.__delay_validate_request__ is True:
                func_kwargs = kwargs
            else:
                func_kwargs = _validate_request(
                    header=header,
                    cookie=cookie,
                    path=path,
                    query=query,
                    form=form,
                    body=body,
                    path_kwargs=kwargs,
                )

            # handle async request
            if view_class:
                signature = inspect.signature(view_class.__init__)
                parameters = signature.parameters
                if parameters.get("view_kwargs"):
                    view_object = view_class(view_kwargs=view_kwargs)  # pragma: no cover
                else:
                    view_object = view_class()
                response = await func(view_object, **func_kwargs)
            else:
                response = await func(**func_kwargs)

            _validate_response = validate_response or current_app.validate_response  # type: ignore

            if _validate_response and responses:  # pragma: no cover
                validate_response_callback = getattr(current_app, "validate_response_callback")
                return validate_response_callback(response, responses)

            return response
    else:

        @wraps(func)
        def view_func(**kwargs) -> FlaskResponse:
            if hasattr(func, "__delay_validate_request__") and func.__delay_validate_request__ is True:
                func_kwargs = kwargs
            else:
                func_kwargs = _validate_request(
                    header=header,
                    cookie=cookie,
                    path=path,
                    query=query,
                    form=form,
                    body=body,
                    path_kwargs=kwargs,
                )

            # handle request
            if view_class:
                signature = inspect.signature(view_class.__init__)
                parameters = signature.parameters
                if parameters.get("view_kwargs"):
                    view_object = view_class(view_kwargs=view_kwargs)
                else:
                    view_object = view_class()
                response = func(view_object, **func_kwargs)
            else:
                response = func(**func_kwargs)

            _validate_response = validate_response or current_app.validate_response  # type: ignore

            if _validate_response and responses:
                validate_response_callback = getattr(current_app, "validate_response_callback")
                return validate_response_callback(response, responses)

            return response

    if not hasattr(func, "view"):
        func.view = view_func

    return func.view
