import json
import os

import maplib.constants as consts


def get_file_basename(file_name):
    return os.path.splitext(file_name)[0]


def get_file_extension(file_name):
    return os.path.splitext(file_name)[1]


def get_relative_path(file_name):
    return os.path.relpath(file_name, consts.REPOSITORY_DIR)


def dump_dict(obj, file_name, indent=0, sort_keys=True):
    """
    Be careful that this function can cover json data.
    """
    with open(file_name, "w", encoding=consts.UTF_8) as output_file:
        json.dump(obj, output_file, indent=indent, sort_keys=sort_keys, ensure_ascii=False)


def copy_file(old_file_name, new_file_name):
    commands = [
        "copy",
        old_file_name,
        new_file_name,
        ">",
        os.devnull
    ]
    os.system(" ".join(commands))
