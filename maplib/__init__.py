from reportlab.graphics import renderPDF
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg

import maplib.parameters as params

from maplib.svg.main_project import Project
from maplib.tools.file_tools import get_file_extension
from maplib.tools.time_ops import timer_decorator


def run_project(metro_input_file, geography_input_file, output_file):
    extension = get_file_extension(output_file)
    svg_output_file = output_file.replace(extension, ".svg")
    Project(metro_input_file, geography_input_file, svg_output_file)
    if extension != ".svg":
        drawing = svg2rlg(svg_output_file)
        if extension == ".pdf":
            renderPDF.drawToFile(drawing, output_file)
        else:
            raise OSError


@timer_decorator()
def main():
    run_project(
        params.METRO_INPUT_FILE_DIR,
        params.GEOGRAPHY_INPUT_FILE_DIR,
        params.OUTPUT_FILE_DIR
    )

