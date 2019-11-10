from maplib.parameters import INPUT_FILE_NAME
from maplib.parameters import OUTPUT_FILE_NAME

from maplib.svg.main_project import Main
from maplib.tools.time_ops import test_time


@test_time
def main():
    Main(INPUT_FILE_NAME, OUTPUT_FILE_NAME)
    
