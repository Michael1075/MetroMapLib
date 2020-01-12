import json
import os

import maplib.constants as consts
import maplib.parameters as params


def get_file_extension(file_name):
    return os.path.splitext(file_name)[1]


def dump_dict(obj, file_name, indent=0, sort_keys=True):
    """
    Be careful that his function can cover json data.
    """
    with open(file_name, "w", encoding=consts.UTF_8) as output_file:
        json.dump(obj, output_file, indent=indent, sort_keys=sort_keys, ensure_ascii=False)


def dump_tex_dict(global_tex_dict):
    dump_dict(global_tex_dict, params.TEX_JSON_DIR)


def copy_file(old_file_name, new_file_name):
    commands = [
        "copy",
        old_file_name,
        new_file_name,
        ">",
        os.devnull
    ]
    os.system(" ".join(commands))


def get_global_tex_dict(use_current_data=False):
    if use_current_data is True:
        with open(params.TEX_JSON_DIR, "r", encoding=consts.UTF_8) as input_file:
            return json.load(input_file)
    if use_current_data is False:
        return params.GLOBAL_TEX_DICT.copy()
    return use_current_data


def get_global_file_dict(use_current_data=False):
    return get_global_tex_dict(use_current_data)["file"]


def get_global_path_dict(use_current_data=False):
    return get_global_tex_dict(use_current_data)["path"]


def get_input_dict(use_current_data=False):
    if use_current_data:
        with open(params.INPUT_JSON_DIR, "r", encoding=consts.UTF_8) as input_file:
            return json.load(input_file)
    return params.INPUT_DATABASE_DICT.copy()
