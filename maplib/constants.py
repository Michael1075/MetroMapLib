from functools import reduce
import numpy as np
import operator as op
import os

from maplib.tools.numpy_type_tools import np_float
from maplib.utils.color import Color


# code author
CODE_AUTHOR = "Michael W"
GITHUB_URL = "https://github.com/Michael1075/MetroMapLib"

# numpy constants
NAN = np.nan
PI = np.pi

# directions
ORIGIN = np_float(0, 0)
RIGHT = np_float(1, 0)
UP = np_float(0, 1)
LEFT = np_float(-1, 0)
DOWN = np_float(0, -1)
RU = RIGHT + UP
LU = LEFT + UP
LD = LEFT + DOWN
RD = RIGHT + DOWN
FOUR_BASE_DIRECTIONS = (RIGHT, UP, LEFT, DOWN)
EIGHT_BASE_DIRECTIONS = (RIGHT, RU, UP, LU, LEFT, LD, DOWN, RD)

# strs
UTF_8 = "utf-8"
HORIZONTAL = "h"
VERTICAL = "v"
CHN = "chn"
ENG = "eng"

# basic colors
WHITE = Color(255, 255, 255)
BLACK = Color(0, 0, 0)

# base settings
DEFAULT_PROJECT_CITY_NAME = "Shanghai"
DECIMAL_DIGITS = 6
TOLERANCE = 1e-8

# dirs
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPOSITORY_DIR = os.path.dirname(THIS_DIR)
FILE_DIR = os.path.join(THIS_DIR, "files")
TEX_CACHE_DIR = os.path.join(FILE_DIR, "tex_cache")
LOGO_DIRS = {
    "railway_station": os.path.join(FILE_DIR, "railway_station.svg"),
    "airport": os.path.join(FILE_DIR, "airport.svg"),
}

# tex base
TEMPLATE_TEX_FILE = os.path.join(FILE_DIR, "tex_template.tex")
with open(TEMPLATE_TEX_FILE, "r") as input_file:
    TEMPLATE_TEX_FILE_BODY = input_file.read()
TEX_TO_REPLACE = "YourTextHere"

# tex fonts
TEX_FONT_CMDS_DICT = {
    CHN: ("songti", "heiti", "lishu", "youyuan", "kaishu", "fangsong"),
    ENG: ("rmfamily", "sffamily", "ttfamily"),
}
TEX_FONT_CMDS = reduce(op.add, TEX_FONT_CMDS_DICT.values())

# options
OPEN_OUTPUT_FILE_AT_ONCE = True
PRINT_TEX_WRITING_PROGRESS_MSG = True
PRINT_FILE_MODIFYING_MSG = True
PRINT_FILE_READY_MSG = True
PRINT_TIMER_MSG = True

# msgs
TEX_WRITING_PROGRESS_MSG = "Writing '{0}'"
SINGLE_TEX_MSG = "{0} - {1}"
GENERATE_SUCCESSFULLY_MSG = "Successfully generated"
GENERATE_UNSUCCESSFULLY_MSG = "Already existed"
REMOVE_SUCCESSFULLY_MSG = "Successfully removed"
REMOVE_UNSUCCESSFULLY_MSG = "Does not exist"
TEX_GENERATE_MEG = "Generating tex..."
TEX_REMOVE_MEG = "Removing tex..."
FORMAT_MSG = "Formatting {0}..."
COPY_MSG = "Copying {0}..."
COPY_FINISH_MSG = "Successfully copied to {0}"
FILE_READY_MSG = "File ready at {0}"
TIMER_MSG = "Consumed time of function {0}: {1:.3f} second(s)"

# help msgs
CMD_PARAMETER_HELP_MSG = "name of your target project file"
