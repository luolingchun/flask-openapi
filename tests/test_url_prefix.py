import pytest

from flask_openapi import APIBlueprint, APIView, OpenAPI

app = OpenAPI(
    __name__,
)
app.config["TESTING"] = True


@pytest.fixture
def client():
    client = app.test_client()

    return client


api1 = APIBlueprint("/book1", __name__, url_prefix="/api")
api2 = APIBlueprint("/book2", __name__)


@api1.get("/book")
def create_book1(): ...


@api2.get("")
def get_book(): ...


@api2.get("/book")
def create_book2(): ...


app.register_api(api1, url_prefix="/api1")
app.register_api(api2, url_prefix="/api2")

api_view1 = APIView(url_prefix="/api")
api_view2 = APIView()


@api_view1.route("/book")
class BookAPIView:
    @api_view1.doc(summary="get book")
    def get(self): ...


@api_view2.route("/book")
class BookAPIView2:
    @api_view2.doc(summary="get book")
    def get(self): ...


app.register_api_view(api_view1, url_prefix="/api3")
app.register_api_view(api_view2, url_prefix="/api4")


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    _json = resp.json
    paths = _json["paths"].keys()
    assert "/api1/book" in paths
    assert "/api2" in paths
    assert "/api2/book" in paths
    assert "/api3/book" in paths
    assert "/api4/book" in paths
