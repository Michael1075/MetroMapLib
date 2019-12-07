import maplib.parameters as params


def remove_list_redundancies(list_obj, equal_func):
    """
    Used instead of list(set(list_obj)) to maintain order
    Keeps the last occurance of each element.
    """
    reversed_result = []
    used = set()
    for element in reversed(list_obj):
        if equal_func(element) not in used:
            reversed_result.append(element)
            used.add(equal_func(element))
    reversed_result.reverse()
    return reversed_result


def merge_dicts(dict1, dict2):
    dict1.update(dict2)
    return dict1


def sort_dict_by_key(dict_obj):
    return {key: dict_obj[key] for key in sorted(dict_obj)}


def get_first_item(vals):
    result_list = [val for val in vals if val is not None]
    result_set = set(result_list)
    if len(result_set) != 1:
        raise ValueError(result_set)
    return result_list[0]


def shrink_value(value, val1, val2):
    """
    Return a value in [val1, val2).
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
    return abs(val1 - val2) < params.TOLERANCE


def modify_num(num):
    num = float(num)
    if close_to(round(num), num):
        return round(num)
    return round(num, params.DECIMAL_DIGITS)


def nums_to_string(nums, separator = " "):
    return separator.join([str(modify_num(val)) for val in nums])


def string_to_nums(string, separator = " "):
    return [eval(val_str) for val_str in string.split(separator)]


def get_path_id_num_str(path_id_name):
    return path_id_name[(path_id_name.index("-") + 1):]


def get_path_id_name(path_id_num, font_type):
    return "g{0}-{1}".format(params.TEX_FONT_CMDS.index(font_type), path_id_num)

