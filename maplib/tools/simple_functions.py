from maplib.parameters import DECIMAL_DIGITS
from maplib.parameters import TOLERANCE


def get_first_item(items):
    assert bool(items)
    for item in items:
        if item is not None:
            return item


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

