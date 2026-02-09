from flask_openapi import OpenAPI

app = OpenAPI(__name__)


@app.route("/")
def hello_world():
    return "Hello, World!"


if __name__ == "__main__":
    app.run()
