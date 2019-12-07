import maplib.constants as consts


def position(x, y):
    return x * consts.RIGHT + y * consts.UP


def position_list(*coords):
    return [position(*coord) for coord in coords]

