import concurrent.futures as ft

import maplib.constants as consts
import maplib.parameters as params

from maplib.svg.misc import NumberNameFrame
from maplib.svg.misc import StringsNameFrame
from maplib.svg.svg_element import Group
from maplib.svg.tex import Tex
from maplib.svg.tex import TexBox
from maplib.svg.tex import TexFileWriter
from maplib.svg.tex import TexGroup
from maplib.tools.json_file_tools import generate_tex_in_json
from maplib.tools.json_file_tools import get_empty_font_type_dict
from maplib.tools.simple_functions import remove_list_redundancies
from maplib.tools.space_ops import get_simplified_direction
from maplib.utils.models import MetroName


class TexNameTemplate(Group):
    body_group_id_name = None
    same_color = True

    def __init__(self, id_name, objs, tex_style):
        self.objs = objs
        self.tex_style = tex_style
        self.sorted_languages = self.get_sorted_languages()
        Group.__init__(self, id_name)
        self.flip_y()
        if "shadow" in self.tex_style.keys():
            self.add_shadow_tex()
        self.add_body_tex()

    def get_aligning_information(self, obj):
        aligned_point = obj.center_point
        aligned_direction = consts.ORIGIN
        return aligned_point, aligned_direction

    def get_color(self, language):
        language_style = self.get_language_style(language)
        return language_style["color"]

    def get_special_color(self, language, obj):
        """
        Implemented in subclasses.
        """
        return self.get_color(language)

    def get_sorted_languages(self):
        language_list = []
        for language, language_style in self.tex_style["languages"].items():
            if language_style["tex_box_index"] is not None:
                language_index = language_style["tex_box_index"]
                language_list.append((language_index, language))
        language_list.sort(key = lambda pair: pair[0])
        return tuple([pair[1] for pair in language_list])

    def get_language_style(self, language):
        return self.tex_style["languages"][language]

    def get_partial_groups(self):
        group_list = []
        for language in self.sorted_languages:
            partial_group = Group(None)
            if self.same_color:
                color = self.get_color(language)
                partial_group.set_style({
                    "fill": color,
                })
            group_list.append(partial_group)
        return group_list

    def get_tex_group(self):
        partial_groups = self.get_partial_groups()
        tex_group = TexGroup(self.body_group_id_name, partial_groups)
        return tex_group

    @staticmethod
    def construct_tex(string_and_cmd):
        string, cmd = string_and_cmd
        writer = TexFileWriter(string, cmd)
        writer.write_directly()
        return writer

    def get_tex_obj_list(self, obj, tex_dict_cache):
        tex_str_dict = obj.get_name_dict()
        tex_obj_list = []
        for language in self.sorted_languages:
            language_style = self.get_language_style(language)
            tex_obj = Tex(
                tex_str_dict[language],
                language_style["font_type"],
                language_style["scale_factor"],
                tex_dict_cache
            )
            if not self.same_color:
                color = self.get_special_color(language, obj)
                tex_obj.set_style({
                    "fill": color
                })
            tex_obj_list.append(tex_obj)
        return tex_obj_list

    @staticmethod
    def get_dict_from_tex_cache(tex_cache):
        empty_dict = get_empty_font_type_dict()
        tex_dict_cache = {
            "file": empty_dict,
            "path": empty_dict,
        }
        return generate_tex_in_json(tex_cache, tex_dict_cache)

    def get_tex_dict_cache(self):
        string_and_cmd_list = []
        for language in self.sorted_languages:
            language_style = self.get_language_style(language)
            font_type = language_style["font_type"]
            for obj in self.objs:
                tex_str_dict = obj.get_name_dict()
                string = tex_str_dict[language]
                string_and_cmd_list.append((string, font_type))
        filtered_string_and_cmd_list = remove_list_redundancies(string_and_cmd_list)
        with ft.ThreadPoolExecutor() as executor:
            tex_cache = list(executor.map(TexNameTemplate.construct_tex, filtered_string_and_cmd_list))
        tex_dict_cache = TexNameTemplate.get_dict_from_tex_cache(tex_cache)
        return tex_dict_cache

    def add_body_tex(self):
        tex_group = self.get_tex_group()
        box_format = self.tex_style["tex_box_format"]
        buff = self.tex_style["tex_buff"]
        tex_dict_cache = self.get_tex_dict_cache()
        tex_objs = []
        for obj in self.objs:
            tex_obj_list = self.get_tex_obj_list(obj, tex_dict_cache)
            aligned_point, aligned_direction = self.get_aligning_information(obj)
            tex_box = TexBox(tex_obj_list, aligned_point, aligned_direction, buff, box_format)
            tex_group.append_tex_box(tex_box)
            for tex_obj in tex_obj_list:
                tex_objs.append(tex_obj)
        self.append(tex_group)
        self.tex_objs = tex_objs
        return self

    def add_shadow_tex(self):
        shadow_style = self.tex_style["shadow"]
        shadow_group = Group(None)
        shadow_group.set_style({
            "fill": None,
            "stroke": shadow_style["color"],
            "stroke-width": shadow_style["stroke_width"] * 2 / params.TEX_BASE_SCALE_FACTOR,
            "stroke-opacity": shadow_style["opacity"],
        })
        shadow_group.use(self.body_group_id_name)
        self.append(shadow_group)
        return self


class StationName(TexNameTemplate):
    body_group_id_name = "station_name_body"

    def __init__(self, id_name, objs):
        TexNameTemplate.__init__(self, id_name, objs, params.STATION_NAME_TEX_STYLE)

    def get_aligning_information(self, station):
        align_buffs = [self.tex_style[key] for key in ("big_buff", "small_buff")]
        label_direction = station.label_direction
        aligned_direction = -label_direction
        align_buff = align_buffs[get_simplified_direction(label_direction) % 2]
        aligned_point = station.frame.get_critical_point(label_direction) + align_buff * label_direction
        return aligned_point, aligned_direction


class GeographicName(Group):
    def __init__(self, id_name, name_objs_dict):
        Group.__init__(self, id_name)
        for name_type, obj_list in name_objs_dict.items():
            name_group = TexNameTemplate(name_type, obj_list, params.GEOGRAPHIC_NAME_TEX_STYLE[name_type])
            self.append(name_group)


class SingleSignName(TexNameTemplate):
    same_color = False

    def __init__(self, id_name, metro_list, tex_style):
        self.metro_list = metro_list
        metro_name_list_dict = self.get_metro_name_list_dict()
        metro_name_objs = []
        for metro_name_list in metro_name_list_dict.values():
            metro_name_objs.extend(metro_name_list)
        self.metro_name_list_dict = metro_name_list_dict
        self.init_template()
        TexNameTemplate.__init__(self, id_name, metro_name_objs, tex_style)

    def get_special_color(self, language, metro_name_obj):
        return metro_name_obj.color

    def get_metro_name_list_dict(self):
        metro_name_list_dict = {}
        for metro in self.metro_list:
            metro_name_list = []
            for name_coord in metro.names_coord:
                metro_name_obj = MetroName(metro, name_coord)
                metro_name_list.append(metro_name_obj)
            metro_name_list_dict[metro.layer_num] = metro_name_list
        return metro_name_list_dict

    def add_body_tex(self):
        tex_group = self.get_tex_group()
        box_format = self.tex_style["tex_box_format"]
        buff = self.tex_style["tex_buff"]
        tex_dict_cache = self.get_tex_dict_cache()
        tex_objs = []
        tex_box_size_dict = {}
        for metro in self.metro_list:
            for obj in self.metro_name_list_dict[metro.layer_num]:
                tex_obj_list = self.get_tex_obj_list(obj, tex_dict_cache)
                aligned_point, aligned_direction = self.get_aligning_information(obj)
                tex_box = TexBox(tex_obj_list, aligned_point, aligned_direction, buff, box_format)
                tex_group.append_tex_box(tex_box)
                tex_box_size_dict[metro.layer_num] = tex_box.box_size
                for tex_obj in tex_obj_list:
                    tex_objs.append(tex_obj)
        self.append(tex_group)
        self.tex_objs = tex_objs
        self.tex_box_size_dict = tex_box_size_dict
        return self


class SignName(Group):
    def __init__(self, id_name, metro_objs):
        Group.__init__(self, id_name)
        self.init_template()
        type_to_metros_dict = {
            "number": [],
            "strings": [],
        }
        for metro in metro_objs:
            name_type = metro.get_name_type()
            type_to_metros_dict[name_type].append(metro)
        for name_type, metro_list in type_to_metros_dict.items():
            name_group = self.get_name_group(name_type, metro_list)
            frame_group = self.get_frame_group(name_type, metro_list, name_group)
            self.append(frame_group)
            self.append(name_group)

    def get_name_group(self, name_type, metro_list):
        return SingleSignName(name_type, metro_list, params.SIGN_TEX_STYLE[name_type])

    def get_frame_group(self, name_type, metro_list, name_group):
        frame_group = Group(None)
        frame_group.set_style({
            "fill-opacity": params.SIGN_NAME_STYLE["fill_opacity"],
        })
        for metro in metro_list:
            if name_type == "number":
                frame_template = NumberNameFrame(metro)
            elif name_type == "strings":
                box_size = name_group.tex_box_size_dict[metro.layer_num]
                frame_template = StringsNameFrame(metro, box_size)
            else:
                raise NotImplementedError(name_type)
            self.template.append(frame_template)
            for coord in metro.names_coord:
                frame_group.use(metro.sign_id_name, coord)
        return frame_group
