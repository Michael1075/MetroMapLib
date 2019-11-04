from parameters import OUTPUT_FILE_NAME

from svg.main_project import Project
from tools.time_ops import test_time
from tools.svg_file_tools import svg_to_pdf


@test_time
def main():
    file_name = OUTPUT_FILE_NAME
    if file_name.endswith(".svg"):
        Project(file_name)
    elif file_name.endswith(".pdf"):
        svg_file_name = file_name.replace(".pdf", ".svg")
        Project(svg_file_name)
        svg_to_pdf(svg_file_name, file_name)
    else:
        raise OSError
    
