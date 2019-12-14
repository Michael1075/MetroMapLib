import numpy as np


def np_float(x, y):
    """
    Only used to get 2D coordinate in float type.
    """
    return np.array((x, y), dtype = "float64")


def np_to_tuple(np_data):
    """
    Converts half-integers to a tuple with integers.
    0.5 -> 1; -0.5 -> -1
    """
    result = np.where(np_data >= 0, np.rint(np_data + 0.1), np.rint(np_data - 0.1))
    return tuple(result.astype("int64"))

