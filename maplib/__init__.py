from reportlab.graphics import renderPDF
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg

from maplib.parameters import INPUT_FILE_DIR
from maplib.parameters import OUTPUT_FILE_DIR

from maplib.svg.main_project import Project
from maplib.tools.file_tools import get_file_extension
from maplib.tools.time_ops import timer_decorator


def run_project(input_file, output_file):
    extension = get_file_extension(output_file)
    svg_output_file = output_file.replace(extension, ".svg")
    Project(input_file, svg_output_file)
    if extension != ".svg":
        drawing = svg2rlg(svg_output_file)
        if extension == ".pdf":
            renderPDF.drawToFile(drawing, output_file)
        else:
            raise OSError


@timer_decorator()
def main():
    run_project(INPUT_FILE_DIR, OUTPUT_FILE_DIR)

