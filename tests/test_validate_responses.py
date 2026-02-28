from __future__ import annotations

from http import HTTPStatus

import pytest
from flask import make_response
from pydantic import BaseModel, ValidationError

from flask_openapi import APIView, OpenAPI
from flask_openapi.blueprint import APIBlueprint


class BaseRequest(BaseModel):
    """Base description"""

    test_int: int
    test_str: str


class GoodResponse(BaseRequest):
    test_int: int
    test_str: str


class BadResponse(BaseModel):
    test_int: str
    test_str: str


def test_no_validate_response(request):
    """
    Response validation defaults to no validation
    Response doesn't match schema and doesn't raise any errors
    """
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    @test_app.post("/test", responses={201: BadResponse})
    def endpoint_test(body: BaseRequest):
        return body.model_dump(), 201

    with test_app.test_client() as client:
        resp = client.post("/test", json={"test_int": 1, "test_str": "s"})
        assert resp.status_code == 201


def test_app_level_validate_response(request):
    """
    Validation turned on at app level
    """
    test_app = OpenAPI(request.node.name, validate_response=True)
    test_app.config["TESTING"] = True

    @test_app.post("/test", responses={200: BadResponse})
    def endpoint_test(body: BaseRequest):
        return body.model_dump_json()

    with test_app.test_client() as client:
        with pytest.raises(ValidationError):
            _ = client.post("/test", json={"test_int": 1, "test_str": "s"})


def test_app_api_level_validate_response(request):
    """
    Validation turned on at app level
    """
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    @test_app.post("/test", responses={HTTPStatus.CREATED: BadResponse}, validate_response=True)
    def endpoint_test(body: BaseRequest):
        return body.model_dump(), HTTPStatus.CREATED

    with test_app.test_client() as client:
        with pytest.raises(ValidationError):
            _ = client.post("/test", json={"test_int": 1, "test_str": "s"})


def test_abp_level_no_validate_response(request):
    """
    Validation turned on at app level
    """
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True
    test_abp = APIBlueprint("abp", __name__)

    @test_abp.post("/test", responses={201: BadResponse})
    def endpoint_test(body: BaseRequest):
        return body.model_dump(), 201

    test_app.register_api(test_abp)

    with test_app.test_client() as client:
        resp = client.post("/test", json={"test_int": 1, "test_str": "s"})
        assert resp.status_code == 201


def test_abp_level_validate_response(request):
    """
    Validation turned on at app level
    """
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True
    test_abp = APIBlueprint("abp", __name__, validate_response=True)

    @test_abp.post("/test", responses={201: BadResponse})
    def endpoint_test(body: BaseRequest):
        return body.model_dump(), 201

    test_app.register_api(test_abp)

    with test_app.test_client() as client:
        with pytest.raises(ValidationError):
            _ = client.post("/test", json={"test_int": 1, "test_str": "s"})


def test_abp_api_level_validate_response(request):
    """
    Validation turned on at app level
    """
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True
    test_abp = APIBlueprint("abp", __name__)

    @test_abp.post("/test", responses={201: BadResponse}, validate_response=True)
    def endpoint_test(body: BaseRequest):
        return body.model_dump(), 201

    test_app.register_api(test_abp)

    with test_app.test_client() as client:
        with pytest.raises(ValidationError):
            _ = client.post("/test", json={"test_int": 1, "test_str": "s"})


def test_apiview_no_validate_response(request):
    """
    Response validation defaults to no validation
    Response doesn't match schema and doesn't raise any errors
    """
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True
    test_api_view = APIView("")

    @test_api_view.route("/test")
    class TestAPI:
        @test_api_view.doc(responses={201: BadResponse})
        def post(self, body: BaseRequest):
            return body.model_dump(), 201

    test_app.register_api_view(test_api_view)

    with test_app.test_client() as client:
        resp = client.post("/test", json={"test_int": 1, "test_str": "s"})
        assert resp.status_code == 201


def test_apiview_app_level_validate_response(request):
    """
    Validation turned on at app level
    """

    test_app = OpenAPI(request.node.name, validate_response=True)
    test_app.config["TESTING"] = True
    test_api_view = APIView("")

    @test_api_view.route("/test")
    class TestAPI:
        @test_api_view.doc(responses={201: BadResponse})
        def post(self, body: BaseRequest):
            return body.model_dump(), 201

    test_app.register_api_view(test_api_view)

    with test_app.test_client() as client:
        with pytest.raises(ValidationError):
            _ = client.post("/test", json={"test_int": 1, "test_str": "s"})


def test_apiview_api_level_validate_response(request):
    """
    Validation turned on at app level
    """

    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True
    test_api_view = APIView("")

    @test_api_view.route("/test")
    class TestAPI:
        @test_api_view.doc(responses={201: BadResponse}, validate_response=True)
        def post(self, body: BaseRequest):
            return body.model_dump(), 201

    test_app.register_api_view(test_api_view)

    with test_app.test_client() as client:
        with pytest.raises(ValidationError):
            _ = client.post("/test", json={"test_int": 1, "test_str": "s"})


def test_validate_response_with_make_response(request):
    test_app = OpenAPI(request.node.name, validate_response=True)
    test_app.config["TESTING"] = True

    @test_app.post("/test1", responses={200: GoodResponse})
    def endpoint_test1():
        r = make_response({"test_int": 1, "test_str": "string"}, 200)
        r.headers["Content-Type"] = "application/json"
        return r

    @test_app.post("/test2", responses={200: GoodResponse})
    def endpoint_test2():
        r = make_response({"test_int": 1, "test_str": "string"}, 200)
        r.headers["Content-Type"] = "application/csv"
        return r

    with test_app.test_client() as client:
        resp = client.post("/test1")
        assert resp.status_code == 200

        resp = client.post("/test2")
        assert resp.status_code == 200


def test_validate_response_with_none(request):
    test_app = OpenAPI(request.node.name, validate_response=True)
    test_app.config["TESTING"] = True

    @test_app.post("/test", responses={204: None})
    def endpoint_test1():
        return "", 204

    with test_app.test_client() as client:
        resp = client.post("/test")
        assert resp.status_code == 204
