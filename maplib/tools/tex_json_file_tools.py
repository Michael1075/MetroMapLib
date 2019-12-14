from functools import reduce
import concurrent.futures as ft
import json
import operator as op
import os

import maplib.parameters as params

from maplib.svg.tex import TexFileWriter
from maplib.tools.file_tools import get_global_tex_dicts
from maplib.tools.simple_functions import remove_list_redundancies
from maplib.tools.time_ops import timer_decorator


def dump_dicts(global_file_dict, global_path_dict):
    """
    Be careful that his function can cover json data.
    """
    with open(params.JSON_TEX_FILE_DEFAULT_DIR, "w") as output_file:
        dump_json(global_file_dict, output_file)
    with open(params.JSON_TEX_PATH_DEFAULT_DIR, "w") as output_file:
        dump_json(global_path_dict, output_file)


def dump_json(obj, file_name):
    return json.dump(obj, file_name, indent = 0, sort_keys = True)


def generate_tex_in_json(generated_tex_objs, global_file_dict, global_path_dict):
    for tex_obj in generated_tex_objs:
        global_file_dict[tex_obj.font_type][str(tex_obj)] = tex_obj.tex_file_dict
        global_path_dict[tex_obj.font_type].update(tex_obj.tex_path_dict)
    return (global_file_dict, global_path_dict)


def remove_tex_in_json(removed_tex_objs, global_file_dict, global_path_dict):
    removed_tex_hash_vals = [str(tex_obj) for tex_obj in removed_tex_objs]
    for tex_obj in removed_tex_objs:
        global_file_dict[tex_obj.font_type].pop(str(tex_obj))
        # Get difference_set to remove path precisely.
        font_file_dict = global_file_dict[tex_obj.font_type]
        old_sets = [
            set(tex_file_dict["h"])
            for tex_file_dict in font_file_dict.values()
        ]
        old_path_num_set = reduce(op.or_, old_sets)
        new_sets = [
            set(tex_file_dict["h"])
            for hash_val, tex_file_dict in font_file_dict.items()
            if hash_val not in removed_tex_hash_vals
        ]
        new_path_num_set = reduce(op.or_, new_sets)
        difference_set = old_path_num_set - new_path_num_set
        for path_num in difference_set:
            global_path_dict[tex_obj.font_type].pop(path_num)
    return (global_file_dict, global_path_dict)


def update_generated_tex_in_json(generated_tex_objs):
    global_file_dict, global_path_dict = get_global_tex_dicts()
    global_file_dict, global_path_dict = generate_tex_in_json(
        generated_tex_objs, global_file_dict, global_path_dict
    )
    dump_dicts(global_file_dict, global_path_dict)


@timer_decorator()
def init_json():
    """
    global_file_dict
    dict_key: tex_font (str)
    dict_val: font_file_dict (dict)
        font_file_dict
        dict_key: hash_val (str)
        dict_val: tex_file_dict (dict)
            tex_file_dict
            {
                "v": viewbox_list (List(float), len 4)
                "h": href_num_list (List(str), len n)*
                "x": x_list (List(float), len n)
                "y": y_list (List(float), len n)
            }
    global_path_dict
    dict_key: tex_font (str)
    dict_val: font_path_dict (dict)
        font_path_dict
        dict_key: path_id_num (str)*
        dict_val: path_string (str)
    * Note, the dict_key in json file should only be a str.
    """
    if params.PRINT_SVG_MODIFYING_MSG:
        print("Initializing json...")
    global_file_dict, global_path_dict = get_global_tex_dicts()
    new_global_file_dict = dict()
    for tex_font, font_file_dict in global_file_dict.items():
        new_font_file_dict = dict()
        for hash_val, tex_file_dict in font_file_dict.items():
            viewbox_list = tex_file_dict["v"]
            href_num_list = tex_file_dict["h"]
            x_list = tex_file_dict["x"]
            y_list = tex_file_dict["y"]
            new_tex_file_dict = {
                "v": viewbox_list,
                "h": href_num_list,
                "x": x_list,
                "y": y_list,
            }
            new_font_file_dict[hash_val] = new_tex_file_dict
        new_global_file_dict[tex_font] = new_font_file_dict
    new_global_path_dict = dict()
    for tex_font, font_path_dict in global_path_dict.items():
        new_font_path_dict = dict()
        for path_id_num, path_string in font_path_dict.items():
            new_path_string = path_string
            new_font_path_dict[path_id_num] = new_path_string
        new_global_path_dict[tex_font] = new_font_path_dict
    dump_dicts(new_global_file_dict, new_global_path_dict)


def create_transcript(file_name_suffix):
    if params.PRINT_SVG_MODIFYING_MSG:
        print("Copying json...")
    for old_file_name in (params.JSON_TEX_FILE_DEFAULT_DIR, params.JSON_TEX_PATH_DEFAULT_DIR):
        new_file_name = old_file_name.replace(".json", file_name_suffix + ".json")
        commands = [
            "copy",
            old_file_name,
            new_file_name,
            ">",
            os.devnull
        ]
        os.system(" ".join(commands))
        if params.PRINT_SVG_MODIFYING_MSG:
            print("Copied to " + new_file_name)


def get_single_tex(tex_obj, generate_file, use_current_data):
    msg_list = [str(tex_obj), tex_obj.tex_string, "-"]
    result = tex_obj.get_dict_if_existed(use_current_data)
    if generate_file:
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
    if params.PRINT_SVG_MODIFYING_MSG:
        print(" ".join(msg_list))
    return tex_obj


@timer_decorator()
def modify_tex(*string_tuples):
    """
    Every string_tuple should contain 3 elements as the following format:
        tuple(
            modify_option: 0 for removing, 1 for generating;
            font_option: either "chn" or "eng",
                or a tuple which consists specified font_types;
            string: a str
        ).
    Judge whether generate or remove based on current json files.
    Generating goes first, then removing.
    """
    if len(string_tuples) == 0:
        return
    generated_tex_objs, removed_tex_objs = string_tuples_to_tex_objs(string_tuples)
    global_file_dict, global_path_dict = get_global_tex_dicts()
    if params.PRINT_SVG_MODIFYING_MSG and generated_tex_objs:
        print("Generating tex...")
    with ft.ThreadPoolExecutor() as executor:
        filtered_generated_tex_objs = [
            tex_obj for tex_obj in executor.map(
                lambda tex_obj: get_single_tex(tex_obj, True, global_file_dict), generated_tex_objs
            ) if tex_obj is not None
        ]
    global_file_dict, global_path_dict = generate_tex_in_json(
        filtered_generated_tex_objs, global_file_dict, global_path_dict
    )
    if params.PRINT_SVG_MODIFYING_MSG and removed_tex_objs:
        print("Removing tex...")
    filtered_removed_tex_objs = [
        tex_obj for tex_obj in map(
            lambda tex_obj: get_single_tex(tex_obj, False, global_file_dict), removed_tex_objs
        ) if tex_obj is not None
    ]
    global_file_dict, global_path_dict = remove_tex_in_json(
        filtered_removed_tex_objs, global_file_dict, global_path_dict
    )
    dump_dicts(global_file_dict, global_path_dict)


def string_tuples_to_tex_objs(string_tuples):
    font_types_dict = {
        "chn": params.TEX_FONT_CMDS_CHN,
        "eng": params.TEX_FONT_CMDS_ENG,
    }
    all_tex_info = []
    for modify_option, font_option, string in string_tuples:
        if modify_option == 1:
            generate_file = True
        elif modify_option == 0:
            generate_file = False
        else:
            raise ValueError(modify_option)
        try:
            font_types = font_types_dict[font_option]
        except KeyError:
            font_types = font_option
        all_tex_info.extend([
            (string, font_type, generate_file)
            for font_type in font_types
        ])
    generated_tex_objs = remove_list_redundancies([
        TexFileWriter(*info[:-1])
        for info in all_tex_info
        if info[-1] is True
    ], str)
    removed_tex_objs = remove_list_redundancies([
        TexFileWriter(*info[:-1])
        for info in all_tex_info
        if info[-1] is False
    ], str)
    return (generated_tex_objs, removed_tex_objs)

