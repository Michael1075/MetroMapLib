from attributes import POINTS_PER_UNIT

import numpy as np


def get_first_item(item_list):
    for item in item_list:
        if item is not None:
            return item
    return


def shrink_value(value, val1, val2):
    """
    Return a value in [val1, val2)
    """
    assert val1 < val2
    result = (value - val1) % (val2 - val1) + val1
    return result


def adjacent_n_tuples(objects, n, loop):
    if loop:
        return zip(*[
            [*objects[k:], *objects[:k]]
            for k in range(n)
        ])
    return zip(*[
        [*objects[k:], *objects[:k]][: 1 - n]
        for k in range(n)
    ])


def get_color_rgb(color):
    if isinstance(color, str):
        return np.array([
            int(color[i : i + 2], 16)
            for i in range(1, 7, 2)
        ]) / 255
    return color


def unit_to_point(unit):
    return unit * POINTS_PER_UNIT


def point_to_unit(point):
    return point / POINTS_PER_UNIT


def modify_point(point, size):
    """
    In order to set the origin in the left bottom of the page
    """
    frame_height = size[1]
    x, y = point
    return np.array([x, frame_height - y])
