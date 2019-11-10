from maplib.constants import RIGHT
from maplib.constants import UP


def position(x, y):
    return x * RIGHT + y * UP


def position_list(*coords):
    return [position(*coord) for coord in coords]

