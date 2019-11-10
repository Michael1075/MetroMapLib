import numpy as np


def np_float(np_data):
    return np_data.astype("float64")


def np_int(np_data):
    """
    It mainly deals with half-integers, like 1.0, 2.0, 1.5,
    however it's tricky when dealing with those ends with .5.
    I decided to let it judge the numbers by 0.4 instead of 0.5.
    And, it's required to make 1.5 and -1.5 get the result with the same absolute value.
    As a result, 1.5 and -1.5 will be changed into 2, -2 respectively.
    """
    result = np.where(np_data >= 0, np.rint(np_data + 0.1), np.rint(np_data - 0.1))
    return result.astype("int64")


def np_to_tuple(np_data):
    return tuple(np_int(np_data))

