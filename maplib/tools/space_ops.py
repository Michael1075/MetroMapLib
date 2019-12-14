import numpy as np

import maplib.constants as consts

from maplib.tools.simple_functions import close_to
from maplib.tools.simple_functions import shrink_value


def arg(point):
    """
    Return a value in [-PI, PI).
    """
    x, y = point
    if x == 0:
        if y == 0:
            return consts.NAN
        if y > 0:
            return consts.PI / 2
        return -consts.PI / 2
    argument = np.arctan(y / x)
    if x < 0:
        if y > 0:
            return argument + consts.PI
        return argument - consts.PI
    return argument


def arg_principle(argument):
    """
    Return a value in [-PI, PI).
    """
    return shrink_value(argument, -consts.PI, consts.PI)


def abs_arg_pair(abs_val, arg_val):
    return scale(rotate(consts.RIGHT, arg_val), abs_val)


def unify_vector(vector):
    abs_val = np.sqrt(sum(vector ** 2))
    return vector / abs_val


def scale_about_origin(point, scale_factor):
    return scale_factor * point


def scale(point, scale_factor, about_point = consts.ORIGIN):
    result = point - about_point
    result = scale_about_origin(result, scale_factor)
    result += about_point
    return result


def rotate_about_origin(point, angle):
    rotation_matrix = get_2D_rotation_matrix(angle)
    return rotation_matrix @ point


def rotate(point, angle, about_point = consts.ORIGIN):
    result = point - about_point
    result = rotate_about_origin(result, angle)
    result += about_point
    return result


def get_2D_rotation_matrix(angle):
    rotation_matrix = np.array([
        [np.cos(angle), -np.sin(angle)],
        [np.sin(angle), np.cos(angle)]
    ])
    return rotation_matrix


def get_2D_line_func_coefficients(point, theta):
    """
    Return (a, b, c) which satisfies a * x + b * y = c.
    """
    x, y = point
    a = np.sin(theta)
    b = -np.cos(theta)
    c = a * x + b * y
    return (a, b, c)


def solve_intersection_point(point1, theta1, point2, theta2):
    a1, b1, c1 = get_2D_line_func_coefficients(point1, theta1)
    a2, b2, c2 = get_2D_line_func_coefficients(point2, theta2)
    A = np.array([[a1, b1], [a2, b2]])
    b = np.array([c1, c2])
    A_rank = np.linalg.matrix_rank(A)
    if A_rank == 2:
        return np.linalg.solve(A, b)
    A_b_rank = np.linalg.matrix_rank(np.c_[A, b[:, None]])
    if A_b_rank == 2:
        return
    return consts.NAN


def center_of_mass(points_list):
    return np.mean(np.array(points_list), axis = 0)


def midpoint(a, b):
    return center_of_mass([a, b])


def get_angle(a, b, c):
    arg_begin = arg(a - b)
    arg_end = arg(c - b)
    return arg_principle(arg_end - arg_begin)


def restore_angle(simplified_angle):
    """
    In simplified angle units, PI is equivalent to 4.
    """
    return simplified_angle * consts.PI / 4


def get_simplified_direction(vector):
    if np.allclose(vector, consts.ORIGIN):
        return consts.NAN
    x, y = vector
    if close_to(x, 0):
        return 2 if y > 0 else -2
    if close_to(y, 0):
        return 0 if x > 0 else -4
    if close_to(x, y):
        return 1 if x > 0 else -3
    if close_to(x, -y):
        return 3 if x < 0 else -1
    return


def get_simplified_angle(a, b, c):
    arg_begin = get_simplified_direction(a - b)
    arg_end = get_simplified_direction(c - b)
    return shrink_value(arg_end - arg_begin, -4, 4)


def num_to_base_direction(num):
    if num not in range(8):
        return
    return consts.EIGHT_BASE_DIRECTIONS[num]


def get_positive_direction(h_or_v):
    if h_or_v == consts.HORIZONTAL:
        return consts.RIGHT
    if h_or_v == consts.VERTICAL:
        return consts.UP
    raise ValueError(h_or_v)


def is_horizontal(direction):
    direction_num = shrink_value(get_simplified_direction(direction) // 2, 0, 2)
    return [True, False][direction_num]

