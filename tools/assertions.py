import numpy as np

from constants import NAN

from tools.simple_functions import adjacent_n_tuples
from tools.space_ops import get_simplified_angle
from tools.space_ops import get_simplified_direction


def assert_true_or_raise(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        assert result is True, func.__name__ + " " + str(result)
    return wrapper


def is_number(data):
    return isinstance(data, (int, float, np.int32, np.int64))


# The parameter required_shape should be a tuple which consists positive integers or None.
# e.g. required_shape = (3, 1, None)
def is_np_data(data, required_dtype = None, required_shape = None):
    if not isinstance(data, np.ndarray):
        return False
    if required_dtype is None:
        if all([
            num_type not in str(data.dtype)
            for num_type in ["int", "float"]
        ]):
            return False
    elif required_dtype != str(data.dtype):
        return False
    if required_shape is None:
        return True
    data_shape = np.shape(data)
    required_dimension = len(required_shape)
    if len(data_shape) != required_dimension:
        return False
    for k in range(required_dimension):
        if required_shape[k] is not None:
            if data_shape[k] != required_shape[k]:
                return False
    return True


@assert_true_or_raise
def is_2D_data(*datum):
    for data in datum:
        if not is_np_data(data, required_shape = (2,)):
            return data
    return True


@assert_true_or_raise
def is_standard_route(points, loop):
    is_2D_data(*points)
    for a, b, c in adjacent_n_tuples(points, 3, loop):
        try:
            simplified_angle = get_simplified_angle(a, b, c)
        except TypeError:
            return b
        if abs(simplified_angle) not in (2, 3):
            return b
    return True


@assert_true_or_raise
def station_on_route(station, points, loop):
    for a, b in adjacent_n_tuples(points, 2, loop):
        direction1 = get_simplified_direction(b - a)
        direction2 = get_simplified_direction(station - a)
        direction3 = get_simplified_direction(b - station)
        if all([
            direction1 is not NAN,
            any([direction2 is NAN, direction2 == direction1]),
            any([direction3 is NAN, direction3 == direction1])
        ]):
            return True
    return station

