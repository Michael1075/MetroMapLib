import json
import os

import maplib.parameters as params


def get_file_extension(file_name):
    return os.path.splitext(file_name)[1]


def get_global_file_dict(use_current_data = False):
    if use_current_data is True:
        with open(params.JSON_TEX_FILE_DEFAULT_DIR, "r") as output_file:
            return json.load(output_file)
    if use_current_data is False:
        return params.GLOBAL_FILE_DICT.copy()
    return use_current_data


def get_global_path_dict(use_current_data = False):
    if use_current_data is True:
        with open(params.JSON_TEX_PATH_DEFAULT_DIR, "r") as output_file:
            return json.load(output_file)
    if use_current_data is False:
        return params.GLOBAL_PATH_DICT.copy()
    return use_current_data


def get_global_tex_dicts(use_current_data = False):
    return (
        get_global_file_dict(use_current_data),
        get_global_path_dict(use_current_data)
    )

