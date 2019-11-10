import os
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg

from maplib.parameters import SVG_HEAD


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


def svg_to_pdf(svg_file_name, pdf_file_name):
    svg_file = svg2rlg(svg_file_name)
    renderPDF.drawToFile(svg_file, pdf_file_name)
    os.remove(svg_file_name)

