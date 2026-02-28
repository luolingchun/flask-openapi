from __future__ import annotations

import pytest

from flask_openapi import OpenAPI

doc_prefix = "/v1/openapi"
app = OpenAPI(__name__, doc_prefix=doc_prefix)
app.config["TESTING"] = True


@pytest.fixture
def client():
    client = app.test_client()

    return client


def test_openapi(client):
    resp = client.get(f"{doc_prefix}/openapi.json")
    assert resp.status_code == 200
    assert resp.json == app.api_doc
