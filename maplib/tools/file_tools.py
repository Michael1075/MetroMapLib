import os

from maplib.parameters import SVG_HEAD


def file_extension(file_name):
    return os.path.splitext(file_name)[1]


def modify(string):
    string = SVG_HEAD + string
    string = string.replace(" />", "/>")
    string = string.replace("><", ">\n<")
    return string


def modify_svg_file(file_name):
    with open(file_name, "r") as input_file:
        string = "".join(input_file.readlines())
    result = modify(string)
    with open(file_name, "w") as output_file:
        output_file.write(result)

