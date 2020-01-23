from functools import reduce
import concurrent.futures as ft
import operator as op

import maplib.constants as consts

from maplib.svg.tex import TexFileWriter
from maplib.tools.file_tools import copy_file
from maplib.tools.file_tools import dump_dict
from maplib.tools.file_tools import get_relative_path
from maplib.tools.simple_functions import remove_list_redundancies
from maplib.tools.time_ops import timer_decorator
from maplib.utils.constructor import Constructor
from maplib.utils.params_getter import Container


class JsonTools(Container):
    @staticmethod
    def get_empty_font_type_dict():
        return {font_type: {} for font_type in consts.TEX_FONT_CMDS}

    def get_global_tex_dict(self):
        return self.params.GLOBAL_TEX_DICT.copy()

    def get_input_dict(self):
        return self.params.INPUT_DATABASE_DICT.copy()

    def dump_tex_dict(self, global_tex_dict):
        dump_dict(global_tex_dict, self.params.TEX_JSON_DIR)

    @staticmethod
    def generate_tex_in_json(generated_tex_objs, global_tex_dict):
        for tex_obj in generated_tex_objs:
            global_tex_dict["file"][tex_obj.font_type][tex_obj.string] = tex_obj.tex_file_dict
            global_tex_dict["path"][tex_obj.font_type].update(tex_obj.tex_path_dict)
        return global_tex_dict

    @staticmethod
    def remove_tex_in_json(removed_tex_objs, global_tex_dict):
        removed_tex_strings = [tex_obj.string for tex_obj in removed_tex_objs]
        for tex_obj in removed_tex_objs:
            global_tex_dict["file"][tex_obj.font_type].pop(tex_obj.string)
            font_file_dict = global_tex_dict["file"][tex_obj.font_type]
            old_sets = [
                set(tex_file_dict["h"])
                for tex_file_dict in font_file_dict.values()
            ]
            old_path_num_set = reduce(op.or_, old_sets)
            new_sets = [
                set(tex_file_dict["h"])
                for string, tex_file_dict in font_file_dict.items()
                if string not in removed_tex_strings
            ]
            new_path_num_set = reduce(op.or_, new_sets)
            difference_set = old_path_num_set - new_path_num_set
            for path_num in difference_set:
                global_tex_dict["path"][tex_obj.font_type].pop(path_num)
        return global_tex_dict

    def update_generated_tex_in_json(self, global_tex_objs):
        generated_tex_objs = remove_list_redundancies(global_tex_objs)
        global_tex_dict = self.get_global_tex_dict()
        new_global_tex_dict = JsonTools.generate_tex_in_json(
            generated_tex_objs, global_tex_dict
        )
        self.dump_tex_dict(new_global_tex_dict)

    @timer_decorator()
    def format_tex_json(self):
        """
        global_tex_dict
            "file": global_file_dict
            dict_key: font_type (str)
            dict_val: font_file_dict (dict)
                font_file_dict
                dict_key: string (str)
                dict_val: tex_file_dict (dict)
                    tex_file_dict
                    {
                        "v": viewbox_list (str) (contains List(float), len 4)
                        "h": href_num_list (str) (contains List(str), len n)
                        "x": x_list (str or float) (contains List(float), len n)
                        "y": y_list (str or float) (contains List(float), len n)
                    }
            "path": global_path_dict
            dict_key: font_type (str)
            dict_val: font_path_dict (dict)
                font_path_dict
                dict_key: path_id_num (str)*
                dict_val: path_string (str)
        * Note, the dict_key in json file should only be a str.
        """
        file_name = self.params.TEX_JSON_DIR
        if consts.PRINT_FILE_MODIFYING_MSG:
            print(consts.FORMAT_MSG.format(get_relative_path(file_name)))
        global_tex_dict = self.get_global_tex_dict()
        new_global_file_dict = JsonTools.get_empty_font_type_dict()
        for font_type, font_file_dict in global_tex_dict["file"].items():
            new_font_file_dict = {}
            for string, tex_file_dict in font_file_dict.items():
                new_tex_file_dict = JsonTools.format_tex_file_dict(tex_file_dict)
                new_font_file_dict[string] = new_tex_file_dict
            new_global_file_dict[font_type] = new_font_file_dict
        new_global_path_dict = JsonTools.get_empty_font_type_dict()
        for font_type, font_path_dict in global_tex_dict["path"].items():
            new_font_path_dict = {}
            for path_id_num, path_string in font_path_dict.items():
                new_path_string = path_string
                new_font_path_dict[path_id_num] = new_path_string
            new_global_path_dict[font_type] = new_font_path_dict
        new_global_tex_dict = {
            "file": new_global_file_dict,
            "path": new_global_path_dict,
        }
        self.dump_tex_dict(new_global_tex_dict)

    @staticmethod
    def format_tex_file_dict(tex_file_dict):
        tex_file_lists = TexFileWriter.tex_file_dict_to_lists(tex_file_dict)
        return TexFileWriter.tex_file_lists_to_dict(*tex_file_lists)

    def create_tex_json_transcript(self, file_name_suffix):
        old_file_name = self.params.TEX_JSON_DIR
        if consts.PRINT_FILE_MODIFYING_MSG:
            print(consts.COPY_MSG.format(get_relative_path(old_file_name)))
        new_file_name = old_file_name.replace(".json", file_name_suffix + ".json")
        copy_file(old_file_name, new_file_name)
        if consts.PRINT_FILE_MODIFYING_MSG:
            print(consts.COPY_FINISH_MSG.format(get_relative_path(new_file_name)))

    @staticmethod
    def get_single_tex(tex_obj, generate_file):
        tex_string = tex_obj.tex_string
        result = tex_obj.get_file_dict_if_existed()
        if generate_file:
            if result is None:
                result_msg = consts.GENERATE_SUCCESSFULLY_MSG
                tex_obj.write_tex_file(result)
            else:
                result_msg = consts.GENERATE_UNSUCCESSFULLY_MSG
                tex_obj = None
        else:
            if result is not None:
                result_msg = consts.REMOVE_SUCCESSFULLY_MSG
            else:
                result_msg = consts.REMOVE_UNSUCCESSFULLY_MSG
                tex_obj = None
        if consts.PRINT_FILE_MODIFYING_MSG:
            print(consts.SINGLE_TEX_MSG.format(tex_string, result_msg))
        return tex_obj

    @timer_decorator()
    def modify_tex_json(self, *string_tuples):
        """
        Every string_tuple should contain 3 elements as the following format:
            tuple(
                modify_option: 0 for removing, 1 for generating;
                font_types: a str or a tuple;
                string: a str
            ).
        Judge whether generate or remove based on current json files.
        Generating goes first, then removing.
        """
        if not string_tuples:
            return
        generated_tex_objs, removed_tex_objs = JsonTools.string_tuples_to_tex_objs(string_tuples)
        global_tex_dict = self.get_global_tex_dict()
        if consts.PRINT_FILE_MODIFYING_MSG and generated_tex_objs:
            print(consts.TEX_GENERATE_MEG)
        with ft.ThreadPoolExecutor() as executor:
            filtered_generated_tex_objs = [
                tex_obj for tex_obj in executor.map(
                    lambda tex_obj: self.get_single_tex(tex_obj, True),
                    generated_tex_objs
                ) if tex_obj is not None
            ]
        global_tex_dict = JsonTools.generate_tex_in_json(
            filtered_generated_tex_objs, global_tex_dict
        )
        if consts.PRINT_FILE_MODIFYING_MSG and removed_tex_objs:
            print(consts.TEX_REMOVE_MEG)
        filtered_removed_tex_objs = [
            tex_obj for tex_obj in map(
                lambda tex_obj: self.get_single_tex(tex_obj, False),
                removed_tex_objs
            ) if tex_obj is not None
        ]
        global_tex_dict = JsonTools.remove_tex_in_json(
            filtered_removed_tex_objs, global_tex_dict
        )
        self.dump_tex_dict(global_tex_dict)

    @staticmethod
    def string_tuples_to_tex_objs(string_tuples):
        all_tex_info = []
        for modify_option, font_types, string in string_tuples:
            if modify_option == 1:
                generate_file = True
            elif modify_option == 0:
                generate_file = False
            else:
                raise ValueError(modify_option)
            if isinstance(font_types, str):
                font_types = (font_types,)
            all_tex_info.extend([
                (string, font_type, generate_file)
                for font_type in font_types
            ])
        generated_tex_objs = remove_list_redundancies([
            TexFileWriter(*info[:-1])
            for info in all_tex_info
            if info[-1] is True
        ])
        removed_tex_objs = remove_list_redundancies([
            TexFileWriter(*info[:-1])
            for info in all_tex_info
            if info[-1] is False
        ])
        return generated_tex_objs, removed_tex_objs

    @timer_decorator()
    def format_input_json(self):
        file_name = self.params.INPUT_JSON_DIR
        if consts.PRINT_FILE_MODIFYING_MSG:
            print(consts.FORMAT_MSG.format(get_relative_path(file_name)))
        input_dict = self.get_input_dict()
        new_metro_database = []
        for metro_dict in input_dict["metro_database"]:
            metro_data = Constructor.get_metro_data(metro_dict)
            new_metro_data = Constructor.format_metro_dict(*metro_data)
            new_metro_database.append(new_metro_data)
        new_name_database = {}
        for name_type, name_data_strs in input_dict["name_database"].items():
            new_name_type = name_type
            name_type_data = Constructor.get_name_type_data(name_data_strs)
            new_name_type_data = Constructor.format_name_type_list(name_type_data)
            new_name_database[new_name_type] = new_name_type_data
        new_geography_database = {}
        for obj_type, objs in input_dict["geography_database"].items():
            new_obj_type = obj_type
            new_obj_type_list = []
            for obj_dict in objs:
                geography_data = Constructor.get_geography_data(obj_dict)
                new_geography_data = Constructor.format_geography_obj_dict(*geography_data)
                new_obj_type_list.append(new_geography_data)
            new_geography_database[new_obj_type] = new_obj_type_list
        new_mark_database = {}
        for mark_type, mark_data_strs in input_dict["mark_database"].items():
            new_mark_type = mark_type
            mark_type_data = Constructor.get_mark_type_data(mark_data_strs)
            new_mark_type_data = Constructor.format_mark_type_list(mark_type_data)
            new_mark_database[new_mark_type] = new_mark_type_data
        new_input_dict = {
            "metro_database": new_metro_database,
            "name_database": new_name_database,
            "geography_database": new_geography_database,
            "mark_database": new_mark_database,
        }
        dump_dict(new_input_dict, file_name, sort_keys=False)

    def create_input_json_transcript(self, file_name_suffix):
        old_file_name = self.params.INPUT_JSON_DIR
        if consts.PRINT_FILE_MODIFYING_MSG:
            print(consts.COPY_MSG.format(get_relative_path(old_file_name)))
        new_file_name = old_file_name.replace(".json", file_name_suffix + ".json")
        copy_file(old_file_name, new_file_name)
        if consts.PRINT_FILE_MODIFYING_MSG:
            print(consts.COPY_FINISH_MSG.format(get_relative_path(new_file_name)))
