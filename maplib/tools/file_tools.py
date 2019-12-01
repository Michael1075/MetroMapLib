from functools import reduce
import json
import os

from maplib.parameters import *


def get_file_extension(file_name):
    return os.path.splitext(file_name)[1]


def dump_json(obj, file_name):
    return json.dump(obj, file_name, indent = 0, sort_keys = True)


def get_global_file_dict(use_current_data):
    if not use_current_data:
        return GLOBAL_FILE_DICT
    with open(JSON_TEX_FILE_DIR, "r") as output_file:
        return json.load(output_file)


def get_global_path_dict(use_current_data):
    if not use_current_data:
        return GLOBAL_PATH_DICT
    with open(JSON_TEX_PATH_DIR, "r") as output_file:
        return json.load(output_file)


def add_tex_to_json(tex_objs, use_current_data = True):
    global_file_dict = get_global_file_dict(use_current_data)
    global_path_dict = get_global_path_dict(use_current_data)
    for tex_obj in tex_objs:
        global_file_dict[tex_obj.font_type][str(tex_obj)] = tex_obj.tex_file_dict
        global_path_dict[tex_obj.font_type].update(tex_obj.tex_path_dict)
    with open(JSON_TEX_FILE_DIR, "w") as output_file:
        dump_json(global_file_dict, output_file)
    with open(JSON_TEX_PATH_DIR, "w") as output_file:
        dump_json(global_path_dict, output_file)


def remove_tex_from_json(tex_objs, use_current_data = True):
    global_file_dict = get_global_file_dict(use_current_data)
    global_path_dict = get_global_path_dict(use_current_data)
    hash_vals = [str(tex_obj) for tex_obj in tex_objs]
    for tex_obj in tex_objs:
        global_file_dict[tex_obj.font_type].pop(str(tex_obj))
        # Get difference_set to remove path precisely
        font_file_dict = global_file_dict[tex_obj.font_type]
        old_sets = [
            set(tex_file_dict["h"])
            for tex_file_dict in font_file_dict.values()
        ]
        old_path_num_set = reduce(lambda a, b: a | b, old_sets)
        new_sets = [
            set(tex_file_dict["h"])
            for hash_val, tex_file_dict in font_file_dict.items()
            if hash_val not in hash_vals
        ]
        new_path_num_set = reduce(lambda a, b: a | b, new_sets)
        difference_set = old_path_num_set - new_path_num_set
        for path_num in difference_set:
            global_path_dict[tex_obj.font_type].pop(path_num)
    with open(JSON_TEX_PATH_DIR, "w") as output_file:
        dump_json(global_path_dict, output_file)
    with open(JSON_TEX_FILE_DIR, "w") as output_file:
        dump_json(global_file_dict, output_file)


def modify_svg_str(string):
    string = SVG_HEAD + string
    string = string.replace(" />", "/>")
    string = string.replace("><", ">\n<")
    return string


def modify_svg_file(file_name):
    with open(file_name, "r") as input_file:
        string = "".join(input_file.readlines())
    result = modify_svg_str(string)
    with open(file_name, "w") as output_file:
        output_file.write(result)

