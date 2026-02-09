from pydantic import BaseModel, Field

from flask_openapi import FileStorage, OpenAPI

app = OpenAPI(__name__)


class UploadFileForm(BaseModel):
    file: FileStorage
    file_type: str = Field(None, description="File Type")


class UploadFilesForm(BaseModel):
    files: list[FileStorage]
    str_list: list[str]
    int_list: list[int]


@app.post("/upload/file")
def upload_file(form: UploadFileForm):
    print(form.file.filename)
    print(form.file_type)
    form.file.save("test.jpg")
    return {"code": 0, "message": "ok"}


@app.post("/upload/files")
def upload_files(form: UploadFilesForm):
    print(form.files)
    print(form.str_list)
    print(form.int_list)
    return {"code": 0, "message": "ok"}


if __name__ == "__main__":
    app.run(debug=True)
