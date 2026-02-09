from flask import make_response

from flask_openapi import OpenAPI

app = OpenAPI(__name__)


@app.get("/image")
def get_image():
    with open("../docs/images/openapi.png", "rb") as f:
        content = f.read()

    r = make_response(content)
    r.mimetype = "image/png"
    return r


if __name__ == "__main__":
    app.run(debug=True)
