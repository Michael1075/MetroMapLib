import os

import maplib.constants as consts

from maplib.svg.main_project import Project
from maplib.tools.file_tools import get_file_extension
from maplib.tools.file_tools import get_relative_path
from maplib.tools.time_ops import timer_decorator
from maplib.utils.params_getter import Container


class MakeProject(Container):
    def __init__(self):
        Container.__init__(self)
        output_file_name = self.params.OUTPUT_SVG_DIR
        self.output_file_name = output_file_name
        extension = get_file_extension(output_file_name)
        if extension != ".svg":
            raise NotImplementedError(extension)
        self.make_project()
        if consts.PRINT_FILE_READY_MSG:
            print(consts.FILE_READY_MSG.format(get_relative_path(output_file_name)))
        if consts.OPEN_OUTPUT_FILE_AT_ONCE:
            self.open_output_file()
    
    @timer_decorator()
    def make_project(self):
        Project()
    
    def open_output_file(self):
        os.system(self.output_file_name)


def main():
    MakeProject()
