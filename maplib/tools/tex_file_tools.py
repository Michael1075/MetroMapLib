import concurrent.futures as ft
import os

from maplib.parameters import TEX_FONT_CMDS_CHN
from maplib.parameters import TEX_FONT_CMDS_ENG

from maplib.svg.tex import TexFileWriter
from maplib.tools.file_tools import add_tex_to_json
from maplib.tools.file_tools import remove_tex_from_json


def get_single_tex(string, font_type, remove_file = False):
    tex_obj = TexFileWriter(string, font_type)
    process_info = "Creating" if not remove_file else "Removing"
    msg_list = [process_info, str(tex_obj), tex_obj.tex_string, "-"]
    result = tex_obj.get_dict_if_existed()
    if not remove_file:
        if result is None:
            result_info = "Successfully generated"
            tex_obj.write_tex_file(result)
        else:
            result_info = "Already existed"
            tex_obj = None
    else:
        if result is not None:
            result_info = "Successfully removed"
        else:
            result_info = "Does not exist"
            tex_obj = None
    msg_list.append(result_info)
    print(" ".join(msg_list))
    return tex_obj


def generate_tex(string, font_types, remove_file = False):
    with ft.ThreadPoolExecutor() as executor:
        filtered_tex_objs = list(filter(
            lambda tex_obj: tex_obj is not None,
            list(executor.map(
                lambda font_type: get_single_tex(string, font_type, remove_file), font_types
            ))
        ))
    if not remove_file:
        add_tex_to_json(filtered_tex_objs)
    else:
        remove_tex_from_json(filtered_tex_objs)


def remove_tex(string, font_types):
    generate_tex(string, font_types, True)


def generate_chn_tex(string):
    generate_tex(string, TEX_FONT_CMDS_CHN)


def generate_eng_tex(string):
    generate_tex(string, TEX_FONT_CMDS_ENG)


def remove_chn_tex(string):
    remove_tex(string, TEX_FONT_CMDS_CHN)


def remove_eng_tex(string):
    remove_tex(string, TEX_FONT_CMDS_ENG)

