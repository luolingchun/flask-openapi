from enum import Enum


class StyleValues(str, Enum):
    matrix = "matrix"
    label = "label"
    form = "form"
    simple = "simple"
    spaceDelimited = "spaceDelimited"
    pipeDelimited = "pipeDelimited"
    deepObject = "deepObject"
