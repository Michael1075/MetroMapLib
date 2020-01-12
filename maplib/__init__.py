import os

import maplib.parameters as params

from maplib.svg.main_project import Project
from maplib.tools.file_tools import get_file_extension
from maplib.tools.time_ops import timer_decorator


class MakeProject(object):
    def __init__(self, output_file_name):
        self.output_file_name = output_file_name
        extension = get_file_extension(output_file_name)
        if extension != ".svg":
            raise NotImplementedError(extension)
        self.make_project()
        if params.PRINT_FILE_READY_MSG:
            print(params.FILE_READY_MSG.format(output_file_name))
        if params.OPEN_OUTPUT_FILE_AT_ONCE:
            self.open_output_file()

    @timer_decorator()
    def make_project(self):
        Project(self.output_file_name)
    
    def open_output_file(self):
        os.system(self.output_file_name)


def main():
    MakeProject(params.OUTPUT_SVG_DIR)
