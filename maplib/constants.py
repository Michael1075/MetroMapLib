import numpy as np

from maplib.tools.numpy_type_tools import np_float
from maplib.utils.color import Color


NAN = np.nan
PI = np.pi

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

HORIZONTAL = "h"
VERTICAL = "v"

CHN = "chn"
ENG = "eng"

WHITE = Color(255, 255, 255)
BLACK = Color(0, 0, 0)

