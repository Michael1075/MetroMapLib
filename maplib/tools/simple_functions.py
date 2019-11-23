from maplib.parameters import DECIMAL_DIGITS
from maplib.parameters import TOLERANCE


def get_first_item(vals):
    result_list = [val for val in vals if val is not None]
    result_set = set(result_list)
    assert len(result_set) == 1, ValueError(result_set)
    return result_list[0]


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


def close_to(val1, val2):
    return abs(val1 - val2) < TOLERANCE


def modify_num(num):
    num = float(num)
    if close_to(round(num), num):
        return round(num)
    return round(num, DECIMAL_DIGITS)


def nums_to_string(nums, separator = " "):
    return separator.join([str(modify_num(val)) for val in nums])


def string_to_nums(string, separator = " "):
    return [eval(val_str) for val_str in string.split(separator)]

