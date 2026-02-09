from flask_openapi.utils import normalize_name


def test_normalize_name():
    assert "List-Generic.Response_Detail_" == normalize_name("List-Generic.Response[Detail]")
