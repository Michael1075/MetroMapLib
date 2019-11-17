from maplib.parameters import INPUT_FILE_NAME
from maplib.parameters import OUTPUT_FILE_NAME

from maplib.svg.main_project import Main
from maplib.tools.process_ops import multiprocess
from maplib.tools.process_ops import multithread
from maplib.tools.time_ops import timer_decorator


@timer_decorator()
def main():
    Main(INPUT_FILE_NAME, OUTPUT_FILE_NAME)

