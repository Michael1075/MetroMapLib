import numpy as np

from tools.color import Color


NAN = np.nan
PI = np.pi

ORIGIN = np.array([0., 0.])
RIGHT = np.array([1., 0.])
UP = np.array([0., 1.])
LEFT = np.array([-1., 0.])
DOWN = np.array([0., -1.])
RU = RIGHT + UP
LU = LEFT + UP
LD = LEFT + DOWN
RD = RIGHT + DOWN
FOUR_BASE_DIRECTIONS = (RIGHT, UP, LEFT, DOWN)
EIGHT_BASE_DIRECTIONS = (RIGHT, RU, UP, LU, LEFT, LD, DOWN, RD)

HORIZONTAL = "h"
VERTICAL = "v"

WHITE = Color(255, 255, 255)
BLACK = Color(0, 0, 0)

