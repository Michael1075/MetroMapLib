import numpy as np

import maplib.constants as consts

from maplib.tools.numpy_type_tools import np_to_tuple
from maplib.tools.simple_functions import adjacent_n_tuples
from maplib.tools.space_ops import get_simplified_angle
from maplib.tools.space_ops import get_simplified_direction


def assert_true_or_raise(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        assert result is True, ValueError(func.__name__ + " " + str(np_to_tuple(result)))
    return wrapper


def is_np_data(data, required_dtype = np.float64, required_shape = None):
    """
    The parameter required_shape should be a tuple consists positive integers or None.
    """
    if not isinstance(data, np.ndarray):
        return False
    if data.dtype != required_dtype:
        return False
    if required_shape is None:
        return True
    if len(data.shape) != len(required_shape):
        return False
    if all([(a == b or b is None) for a, b in zip(data.shape, required_shape)]):
        return True
    return False


def assert_type(val, valid_type):
    assert isinstance(val, valid_type), TypeError(val)


def assert_length(vals, valid_length):
    assert len(vals) == valid_length, ValueError(vals)


@assert_true_or_raise
def assert_is_2D_data(data):
    if not is_np_data(data, required_shape = (2,)):
        return data
    return True


@assert_true_or_raise
def assert_is_standard_route(points, loop):
    for point in points:
        assert_is_2D_data(point)
    for a, b, c in adjacent_n_tuples(points, 3, loop):
        try:
            simplified_angle = get_simplified_angle(a, b, c)
        except TypeError:
            return b
        if abs(simplified_angle) not in (2, 3):
            return b
    return True


@assert_true_or_raise
def assert_station_on_route(station, points, loop):
    for a, b in adjacent_n_tuples(points, 2, loop):
        direction1 = get_simplified_direction(b - a)
        direction2 = get_simplified_direction(station - a)
        direction3 = get_simplified_direction(b - station)
        if all([
            direction1 is not consts.NAN,
            any([direction2 is consts.NAN, direction2 == direction1]),
            any([direction3 is consts.NAN, direction3 == direction1])
        ]):
            return True
    return station

