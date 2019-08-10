from functools import reduce
import numpy as np
import operator as op

from constants import *

from tools.numpy_type_tools import int64

from tools.simple_functions import shrink_value


def abs_C(point):
    x, y = point
    return (x ** 2 + y ** 2) ** 0.5


def arg_C(point):
    """
    Return a value in [-PI, PI)
    """
    x, y = point
    if x == 0:
        if y == 0:
            return np.nan
        if y > 0:
            return PI / 2
        return -PI / 2
    arg = np.arctan(y / x)
    if x < 0:
        if y > 0:
            return arg + PI
        return arg - PI
    return arg


def arg_principle(arg):
    """
    Return a value in [-PI, PI)
    """
    return shrink_value(arg, -PI, PI)


def abs_arg_pair(abs_val, arg_val):
    return scale(rotate(RIGHT, arg_val), abs_val)


def shift(point, *vectors):
    total_vector = reduce(op.add, vectors)
    return point + total_vector


def flip_about_x_axis(point):
    x, y = point
    return np.array([x, -y])


def scale_about_origin(point, scale_factor):
    point *= scale_factor
    return point


def scale(point, scale_factor, about_point = ORIGIN):
    point = shift(point, -about_point)
    point = scale_about_origin(point, scale_factor)
    point = shift(point, about_point)
    return point


def rotate_about_origin(point, angle):
    rotation_matrix = get_2D_rotation_matrix(angle)
    point = rotation_matrix @ point
    return point


def rotate(point, angle, about_point = ORIGIN):
    point = shift(point, -about_point)
    point = rotate_about_origin(point, angle)
    point = shift(point, about_point)
    return point


def get_2D_rotation_matrix(angle):
    rotation_matrix = np.array([
        [np.cos(angle), -np.sin(angle)],
        [np.sin(angle), np.cos(angle)]
    ])
    return rotation_matrix


def get_2D_line_func_coefficients(point, theta):
    """
    Return (a, b, c),
    which satisfies a * x + b * y = c and c = 0 or 1
    """
    x, y = point
    a = np.sin(theta)
    b = -np.cos(theta)
    c = np.sin(theta) * x - np.cos(theta) * y
    return (a, b, c)


def solve_intersection_point(point1, theta1, point2, theta2):
    a1, b1, c1 = get_2D_line_func_coefficients(point1, theta1)
    a2, b2, c2 = get_2D_line_func_coefficients(point2, theta2)
    A = np.array([[a1, b1], [a2, b2]])
    b = np.array([c1, c2])
    A_rank = np.linalg.matrix_rank(A)
    if A_rank == 2:
        return np.linalg.solve(A, b)
    A_b_rank = np.linalg.matrix_rank(np.c_[A, b[:,None]])
    if A_b_rank == 2:
        return
    return np.nan


def midpoint(a, b):
    return (a + b) / 2


def get_angle(a, b, c):
    arg_begin = arg_C(a - b)
    arg_end = arg_C(c - b)
    return arg_principle(arg_end - arg_begin)


# 8 directions: In simplified angle units, PI is equivalent to 4
# 4 directions: Base vectors are RIGHT, LEFT, UP, DOWN
# 2 directions: "h" for horizontal, "v" for vertical


# 8 directions

def get_simplified_direction(vector):
    vector = int64(vector)
    if all(vector == ORIGIN):
        return np.nan
    x, y = vector
    if x == 0:
        return 2 if y > 0 else -2
    if y == 0:
        return 0 if x > 0 else -4
    if x == y:
        return 1 if x > 0 else -3
    if x == -y:
        return 3 if x < 0 else -1
    return


def get_simplified_angle(a, b, c):
    arg_begin = get_simplified_direction(a - b)
    arg_end = get_simplified_direction(c - b)
    return shrink_value(arg_end - arg_begin, -4, 4)


def num_to_base_direction(num):
    if num is None:
        return
    base_directions = (
        RIGHT,
        RU,
        UP,
        LU,
        LEFT,
        LD,
        DOWN,
        RD
    )
    return base_directions[num]


# 4 directions

def get_base_direction(vector):
    vector = int64(vector)
    if all(vector == ORIGIN):
        return np.nan
    x, y = vector
    if x == 0:
        return UP if y > 0 else DOWN
    if y == 0:
        return RIGHT if x > 0 else LEFT
    return


def judge_direction(base_vector):
    if base_vector is RIGHT:
        return ("h", True)
    if base_vector is LEFT:
        return ("h", False)
    if base_vector is UP:
        return ("v", True)
    if base_vector is DOWN:
        return ("v", False)
    return


# 2 directions

def get_positive_direction(direction):
    assert direction in ("h", "v")
    result = RIGHT if direction == "h" else UP
    return result


def get_critical_point_about_center_vector(direction, box_size):
    """
    Picture a box bounding the mobject.
    Such a box has 9 'critical points': 4 corners, 4 edge center, the center.
    This returns one of them.
    """
    assert np.allclose(abs(abs(direction) - np.array([0.5, 0.5])), np.array([0.5, 0.5]))
    vector = direction * box_size / 2
    return vector
