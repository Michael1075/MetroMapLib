import os

import maplib.parameters as params

from maplib.svg.main_project import Project
from maplib.tools.file_tools import get_file_extension
from maplib.tools.time_ops import timer_decorator


class MakeProject(object):
    def __init__(self, output_file):
        self.output_file = output_file
        extension = get_file_extension(output_file)
        assert extension == ".svg", NotImplementedError(extension)
        self.make_project()
        if params.PRINT_FILE_READY_MSG:
            print(params.FILE_READY_MSG.format(output_file))
        if params.OPEN_OUTPUT_FILE_AT_ONCE:
            self.open_output_file()

    @timer_decorator()
    def make_project(self):
        Project(self.output_file)
    
    def open_output_file(self):
        os.system(self.output_file)


def main():
    MakeProject(params.OUTPUT_FILE_DIR)

